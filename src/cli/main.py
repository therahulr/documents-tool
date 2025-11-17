"""
Main CLI module for the synthetic document generator.

This module orchestrates the document generation process.
"""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import yaml

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src.cli.prompts import DocumentGeneratorPrompts
from src.generators import get_generator, GENERATOR_NAMES
from src.formats import get_writer, is_format_supported
from src.utils.size_estimator import SizeEstimator
from src.utils.filename_generator import DocumentNameGenerator


console = Console()


class DocumentGeneratorCLI:
    """
    Main CLI application for synthetic document generation.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize CLI.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.prompts = DocumentGeneratorPrompts()
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {},
        }

    def _load_config(self, config_path: str = None) -> Dict:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            dict: Configuration
        """
        default_config = {
            'output': {
                'directory': './output',
            },
            'generation': {
                'random_seed': None,
                'default_count': 5,
            },
            'data': {
                'locale': 'en_US',
            },
            'size_estimation': {
                'tolerance': 0.15,
                'max_iterations': 100,
            },
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Merge with defaults
                    default_config.update(user_config or {})
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")

        return default_config

    def run(self):
        """
        Run the interactive CLI.
        """
        try:
            # Welcome
            self.prompts.show_welcome()

            # Step 1: Select document types
            selected_types = self.prompts.select_document_types()

            # Step 2: Select formats for each type
            format_selections = {}
            for doc_type in selected_types:
                formats = self.prompts.select_formats(doc_type)
                format_selections[doc_type] = formats

            # Step 3: Configure output
            output_config = self.prompts.configure_output()

            # Step 4: Configure generation (count vs size)
            gen_config = self.prompts.configure_generation()

            # Step 5: Configure document complexity
            complexity_config = self.prompts.configure_document_complexity(selected_types)

            # Build complete configuration
            run_config = {
                'selected_types': selected_types,
                'formats': format_selections,
                'output': output_config,
                'generation': gen_config,
                'complexity': complexity_config,
            }

            # Merge complexity settings into main config for generators
            self.config.update({
                'complexity': complexity_config,
                'num_pages_min': complexity_config['num_pages_min'],
                'num_pages_max': complexity_config['num_pages_max'],
                'num_transactions_min': complexity_config['num_transactions_min'],
                'num_transactions_max': complexity_config['num_transactions_max'],
                'num_excel_rows_max': complexity_config['num_excel_rows_max'],
                'include_charts': complexity_config['include_charts'],
            })

            # Step 6: Show summary and confirm
            if not self.prompts.show_summary(run_config):
                console.print("[yellow]Generation cancelled by user.[/yellow]")
                return

            # Step 7: Generate documents
            self.prompts.show_progress_header()
            start_time = time.time()

            self._generate_documents(run_config)

            duration = time.time() - start_time
            self.stats['duration'] = duration
            self.stats['output_dir'] = run_config['output']['directory']
            self.stats['total_size_str'] = SizeEstimator.format_size(self.stats['total_size'])

            # Step 7: Show completion summary
            self.prompts.show_completion_summary(self.stats)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        except Exception as e:
            self.prompts.show_error(str(e))
            raise

    def _generate_documents(self, config: Dict):
        """
        Generate documents based on configuration.

        Args:
            config: Generation configuration
        """
        output_dir = Path(config['output']['directory'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Calculate total combinations
        combinations = []
        for doc_type in config['selected_types']:
            for fmt in config['formats'][doc_type]:
                combinations.append((doc_type, fmt))

        if config['generation']['mode'] == 'count':
            total_tasks = len(combinations) * config['generation']['count']
        else:
            # For size-based, we don't know exact count
            total_tasks = None

        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            if total_tasks:
                task = progress.add_task("[cyan]Generating documents...", total=total_tasks)
            else:
                task = progress.add_task("[cyan]Generating documents...", total=None)

            if config['generation']['mode'] == 'count':
                self._generate_by_count(
                    combinations, config['generation']['count'],
                    output_dir, progress, task
                )
            else:
                self._generate_by_size(
                    combinations, config['generation']['target_size'],
                    output_dir, progress, task
                )

    def _generate_by_count(
        self,
        combinations: List[tuple],
        count: int,
        output_dir: Path,
        progress: Progress,
        task
    ):
        """
        Generate documents by count.

        Args:
            combinations: List of (doc_type, format) tuples
            count: Number of documents per combination
            output_dir: Output directory
            progress: Progress bar
            task: Progress task
        """
        for doc_type, fmt in combinations:
            for i in range(count):
                self._generate_single_document(doc_type, fmt, output_dir, i)
                progress.update(task, advance=1)

    def _generate_by_size(
        self,
        combinations: List[tuple],
        target_size_str: str,
        output_dir: Path,
        progress: Progress,
        task
    ):
        """
        Generate documents until target size is reached.

        Args:
            combinations: List of (doc_type, format) tuples
            target_size_str: Target size string (e.g., "10MB")
            output_dir: Output directory
            progress: Progress bar
            task: Progress task
        """
        target_size = SizeEstimator.parse_size_string(target_size_str)
        current_size = 0
        iteration = 0
        max_iterations = self.config.get('size_estimation', {}).get('max_iterations', 1000)

        while current_size < target_size and iteration < max_iterations:
            # Cycle through combinations
            doc_type, fmt = combinations[iteration % len(combinations)]

            file_size = self._generate_single_document(doc_type, fmt, output_dir, iteration)
            current_size += file_size

            progress.update(
                task,
                description=f"[cyan]Generating documents... ({SizeEstimator.format_size(current_size)} / {target_size_str})"
            )

            iteration += 1

    def _generate_single_document(
        self,
        doc_type: str,
        fmt: str,
        output_dir: Path,
        counter: int
    ) -> int:
        """
        Generate a single document.

        Args:
            doc_type: Document type
            fmt: Format extension
            output_dir: Output directory
            counter: Counter for unique filenames

        Returns:
            int: File size in bytes
        """
        # Generate content
        generator = get_generator(doc_type, config=self.config, seed=self.config.get('generation', {}).get('random_seed'))
        content = generator.generate_content()

        # Create realistic filename
        filename = DocumentNameGenerator.generate_filename(doc_type, fmt)
        filepath = output_dir / filename

        # Ensure uniqueness by appending counter if file exists
        if filepath.exists():
            base_name = filepath.stem
            filepath = output_dir / f"{base_name}_{counter:03d}.{fmt}"

        # Write document
        writer = get_writer(str(filepath))
        writer.write(content, doc_type)

        # Update statistics
        file_size = filepath.stat().st_size if filepath.exists() else 0
        self.stats['total_files'] += 1
        self.stats['total_size'] += file_size

        if doc_type not in self.stats['by_type']:
            self.stats['by_type'][doc_type] = 0
        self.stats['by_type'][doc_type] += 1

        return file_size


def main(config_path: str = None):
    """
    Main entry point for the CLI.

    Args:
        config_path: Path to configuration file
    """
    cli = DocumentGeneratorCLI(config_path)
    cli.run()


if __name__ == '__main__':
    main()
