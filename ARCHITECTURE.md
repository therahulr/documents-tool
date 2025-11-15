# Synthetic Document Generator - Architecture

## Library Selection Rationale

### Core Document Formats

1. **PDF Generation: `reportlab`**
   - Mature, stable library (20+ years)
   - Precise control over layout, positioning, styling
   - Supports tables, images, multi-page documents
   - License: BSD
   - Active maintenance, extensive documentation

2. **DOCX: `python-docx`**
   - De facto standard for Word document generation
   - Clean API, well-documented
   - Supports paragraphs, tables, headers/footers, styling
   - License: MIT
   - Actively maintained by community

3. **XLSX: `openpyxl`**
   - Full-featured Excel library (read + write)
   - Supports styling, formulas, charts
   - Better for complex spreadsheets than xlsxwriter
   - License: MIT
   - Active development

4. **MSG (Outlook Email): `extract-msg` + Custom**
   - Will generate standard `.eml` format (RFC 5322) using Python's built-in `email` library
   - For `.msg` format: use `msg-writer` or custom implementation using `olefile`
   - MSG format is proprietary but well-documented
   - License: MIT (for supporting libraries)

5. **ODT (OpenDocument): `odfpy`**
   - Official Python library for ODF format
   - Supports text documents with styling
   - License: Apache 2.0 / GPL
   - Maintained by ODF community

6. **Images: `Pillow`**
   - Industry standard for Python image manipulation
   - Can render text, tables, logos onto images
   - Supports JPEG, PNG, and other formats
   - License: HPND (open source)
   - Very actively maintained

### Supporting Libraries

7. **Synthetic Data: `faker`**
   - Most popular synthetic data library
   - Extensive providers (names, addresses, companies, etc.)
   - Locale support (en_US for American-style data)
   - License: MIT
   - Very active, 60k+ stars on GitHub

8. **CLI Enhancement: `rich`**
   - Beautiful terminal UI components
   - Progress bars, tables, colored text, panels
   - Dramatically improves UX
   - License: MIT
   - Actively maintained by Textualize

9. **Configuration: `pyyaml`**
   - Standard YAML parser for Python
   - Clean config file format
   - License: MIT

## Architecture Overview

### Module Structure

```
documents-tool/
├── src/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py          # CLI entry point and menu system
│   │   └── prompts.py       # User interaction prompts
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base generator class
│   │   ├── bank_statement.py
│   │   ├── credit_card_statement.py
│   │   ├── payment_advice.py
│   │   ├── terms_conditions.py
│   │   ├── notification.py
│   │   └── email.py
│   ├── formats/
│   │   ├── __init__.py
│   │   ├── pdf_writer.py    # PDF format implementation
│   │   ├── docx_writer.py   # Word format implementation
│   │   ├── xlsx_writer.py   # Excel format implementation
│   │   ├── msg_writer.py    # Outlook email format
│   │   ├── odt_writer.py    # OpenDocument format
│   │   └── image_writer.py  # Image format (JPEG/PNG)
│   ├── data/
│   │   ├── __init__.py
│   │   ├── synthetic.py     # Synthetic data generators
│   │   └── templates.py     # Document content templates
│   └── utils/
│       ├── __init__.py
│       ├── watermark.py     # Watermark injection
│       ├── formatting.py    # Currency, date formatting
│       └── size_estimator.py # File size estimation
├── config/
│   └── default_config.yaml  # Default configuration
├── tests/
│   ├── __init__.py
│   ├── test_generators.py
│   └── test_formats.py
├── output/                   # Generated documents
├── requirements.txt
├── README.md
└── generate_docs.py         # Main entry point
```

### Design Patterns

1. **Strategy Pattern**: Different format writers implement common interface
2. **Factory Pattern**: Generator registry for creating document generators
3. **Template Method**: Base generator class with hooks for customization
4. **Builder Pattern**: Document content assembled step-by-step

### Key Design Principles

1. **Separation of Concerns**:
   - Generators create document content (data structure)
   - Writers render content to specific formats
   - Clear boundary between "what" and "how"

2. **Extensibility**:
   - Add new document types: create new generator in `generators/`
   - Add new formats: create new writer in `formats/`
   - Registry pattern allows automatic discovery

3. **Configurability**:
   - YAML config for defaults
   - CLI overrides config
   - Environment-specific settings

4. **Testability**:
   - Pure functions for data generation
   - Mock-friendly interfaces
   - Deterministic output with seed control

### Data Flow

```
User Input (CLI)
    ↓
Configuration Merge (CLI + YAML + defaults)
    ↓
Document Type Selection
    ↓
Generator Selection (from registry)
    ↓
Content Generation (synthetic data)
    ↓
Format Writer Selection
    ↓
Document Rendering (with watermark)
    ↓
File Writing (size tracking)
    ↓
Progress Report
```

### Watermark Strategy

The watermark text:
> "This synthetic document is generated by Rahul Raj for testing purpose."

Implementation per format:
- **PDF**: Header/footer on each page using reportlab canvas
- **DOCX**: Header section in document
- **XLSX**: First row (merged cells) with bold formatting
- **MSG/EML**: First line of email body
- **ODT**: Header section
- **Images**: Top banner with semi-transparent background

### Size Control Strategy

1. **Size Estimation**:
   - Empirical formulas based on content volume
   - PDF: ~5KB per page base + content
   - XLSX: ~1KB per row + overhead
   - DOCX: ~10KB base + ~500 bytes per paragraph
   - Images: Width × Height × bytes_per_pixel / compression

2. **Size Targeting**:
   - Generate content incrementally
   - Check estimated size after each addition
   - Stop when target reached (within tolerance)
   - Fallback: max iterations to prevent infinite loops

### Realism Features

1. **Coherent Data**:
   - Running balances in bank statements
   - Date-ordered transactions
   - Realistic merchant names and categories
   - Proper currency formatting

2. **Domain Logic**:
   - Credit card statements: purchases + payments + interest
   - Bank statements: deposits, withdrawals, fees, interest
   - Payment advice: invoice references, line items, taxes

3. **Visual Polish**:
   - Proper formatting (tables, alignment)
   - Logos (synthetic company logos)
   - Headers and footers
   - Page numbering

4. **No Placeholders**:
   - No lorem ipsum
   - No trivial sequences (123456, 000000)
   - Faker-generated realistic data
   - Custom domain-specific generators
