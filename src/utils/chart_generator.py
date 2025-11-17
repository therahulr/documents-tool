"""
Chart and visualization generator.

Creates professional financial charts and visualizations for documents.
"""

import io
import random
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None

from PIL import Image, ImageDraw, ImageFont

from src.utils.watermark import WATERMARK_TEXT


class ChartGenerator:
    """
    Generates various types of financial charts and visualizations.
    """

    # Color schemes for professional charts
    COLOR_SCHEMES = {
        'professional': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'corporate': ['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600'],
        'financial': ['#084594', '#2171b5', '#4292c6', '#6baed6', '#9ecae1'],
        'earth': ['#8c510a', '#bf812d', '#dfc27d', '#80cdc1', '#35978f'],
    }

    @classmethod
    def generate_line_chart(
        cls,
        data: List[Tuple[datetime, float]],
        title: str,
        xlabel: str = "Date",
        ylabel: str = "Amount ($)",
        width: int = 800,
        height: int = 600,
        color_scheme: str = 'professional'
    ) -> Image.Image:
        """
        Generate a line chart.

        Args:
            data: List of (date, value) tuples
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            width: Image width in pixels
            height: Image height in pixels
            color_scheme: Color scheme name

        Returns:
            PIL Image: Generated chart
        """
        if not MATPLOTLIB_AVAILABLE:
            return cls._generate_placeholder_chart(width, height, "Line Chart - Matplotlib not available")

        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

        # Extract dates and values
        dates = [d[0] for d in data]
        values = [d[1] for d in data]

        # Plot
        colors = cls.COLOR_SCHEMES.get(color_scheme, cls.COLOR_SCHEMES['professional'])
        ax.plot(dates, values, color=colors[0], linewidth=2, marker='o', markersize=4)

        # Formatting
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.xticks(rotation=45)

        # Add watermark
        fig.text(0.5, 0.02, WATERMARK_TEXT, ha='center', fontsize=8, alpha=0.5)

        plt.tight_layout()

        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)

        return img

    @classmethod
    def generate_bar_chart(
        cls,
        categories: List[str],
        values: List[float],
        title: str,
        xlabel: str = "Category",
        ylabel: str = "Amount ($)",
        width: int = 800,
        height: int = 600,
        color_scheme: str = 'corporate'
    ) -> Image.Image:
        """
        Generate a bar chart.

        Args:
            categories: List of category names
            values: List of values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            width: Image width
            height: Image height
            color_scheme: Color scheme name

        Returns:
            PIL Image: Generated chart
        """
        if not MATPLOTLIB_AVAILABLE:
            return cls._generate_placeholder_chart(width, height, "Bar Chart - Matplotlib not available")

        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

        # Colors
        colors = cls.COLOR_SCHEMES.get(color_scheme, cls.COLOR_SCHEMES['corporate'])
        bar_colors = [colors[i % len(colors)] for i in range(len(categories))]

        # Plot
        bars = ax.bar(categories, values, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}',
                   ha='center', va='bottom', fontsize=9)

        # Formatting
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')

        # Add watermark
        fig.text(0.5, 0.02, WATERMARK_TEXT, ha='center', fontsize=8, alpha=0.5)

        plt.tight_layout()

        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)

        return img

    @classmethod
    def generate_pie_chart(
        cls,
        labels: List[str],
        values: List[float],
        title: str,
        width: int = 800,
        height: int = 600,
        color_scheme: str = 'financial'
    ) -> Image.Image:
        """
        Generate a pie chart.

        Args:
            labels: List of labels
            values: List of values
            title: Chart title
            width: Image width
            height: Image height
            color_scheme: Color scheme name

        Returns:
            PIL Image: Generated chart
        """
        if not MATPLOTLIB_AVAILABLE:
            return cls._generate_placeholder_chart(width, height, "Pie Chart - Matplotlib not available")

        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

        # Colors
        colors = cls.COLOR_SCHEMES.get(color_scheme, cls.COLOR_SCHEMES['financial'])

        # Plot
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        # Title
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Add watermark
        fig.text(0.5, 0.02, WATERMARK_TEXT, ha='center', fontsize=8, alpha=0.5)

        plt.tight_layout()

        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)

        return img

    @classmethod
    def generate_financial_dashboard(
        cls,
        metrics: Dict[str, Any],
        width: int = 1200,
        height: int = 800
    ) -> Image.Image:
        """
        Generate a financial dashboard with multiple charts.

        Args:
            metrics: Dictionary with financial metrics
            width: Dashboard width
            height: Dashboard height

        Returns:
            PIL Image: Generated dashboard
        """
        if not MATPLOTLIB_AVAILABLE:
            return cls._generate_placeholder_chart(width, height, "Dashboard - Matplotlib not available")

        fig = plt.figure(figsize=(width/100, height/100), dpi=100)

        # Create 2x2 grid
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Chart 1: Revenue trend (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        dates = metrics.get('trend_dates', [])
        revenues = metrics.get('revenues', [])
        if dates and revenues:
            ax1.plot(dates, revenues, color='#1f77b4', linewidth=2)
            ax1.set_title('Revenue Trend', fontweight='bold')
            ax1.set_ylabel('Revenue ($)')
            ax1.grid(True, alpha=0.3)

        # Chart 2: Expense breakdown (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        expense_categories = metrics.get('expense_categories', ['Operating', 'Marketing', 'R&D', 'Admin'])
        expense_values = metrics.get('expense_values', [40000, 25000, 20000, 15000])
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        ax2.pie(expense_values, labels=expense_categories, autopct='%1.1f%%', colors=colors)
        ax2.set_title('Expense Breakdown', fontweight='bold')

        # Chart 3: Monthly comparison (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        months = metrics.get('months', ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'])
        current_year = metrics.get('current_year', [120, 135, 145, 160, 155, 170])
        previous_year = metrics.get('previous_year', [100, 115, 125, 140, 135, 150])
        x = range(len(months))
        width_bar = 0.35
        ax3.bar([i - width_bar/2 for i in x], current_year, width_bar, label='2024', color='#1f77b4')
        ax3.bar([i + width_bar/2 for i in x], previous_year, width_bar, label='2023', color='#ff7f0e')
        ax3.set_title('YoY Comparison', fontweight='bold')
        ax3.set_ylabel('Revenue ($K)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(months)
        ax3.legend()
        ax3.grid(True, axis='y', alpha=0.3)

        # Chart 4: KPIs (bottom right)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        kpis = metrics.get('kpis', {
            'Total Revenue': '$1.2M',
            'Net Profit': '$340K',
            'Growth Rate': '+23.5%',
            'Customer Count': '12,450'
        })
        y_pos = 0.8
        for label, value in kpis.items():
            ax4.text(0.1, y_pos, label + ':', fontsize=12, fontweight='bold')
            ax4.text(0.6, y_pos, value, fontsize=12, color='#1f77b4')
            y_pos -= 0.2

        # Main title
        fig.suptitle('Financial Dashboard', fontsize=16, fontweight='bold', y=0.98)

        # Watermark
        fig.text(0.5, 0.01, WATERMARK_TEXT, ha='center', fontsize=10, alpha=0.5)

        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)

        return img

    @classmethod
    def _generate_placeholder_chart(cls, width: int, height: int, message: str) -> Image.Image:
        """
        Generate a placeholder chart when matplotlib is not available.

        Args:
            width: Image width
            height: Image height
            message: Message to display

        Returns:
            PIL Image: Placeholder image
        """
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # Border
        draw.rectangle([(10, 10), (width-10, height-10)], outline='#cccccc', width=2)

        # Text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Center the message
        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        draw.text((x, y), message, fill='#666666', font=font)

        # Watermark
        try:
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            small_font = font

        bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=small_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) / 2, height - 30), WATERMARK_TEXT, fill='#999999', font=small_font)

        return img


def generate_sample_chart(chart_type: str = 'line', width: int = 800, height: int = 600) -> Optional[Image.Image]:
    """
    Generate a sample chart for testing.

    Args:
        chart_type: Type of chart ('line', 'bar', 'pie', 'dashboard')
        width: Chart width
        height: Chart height

    Returns:
        PIL Image or None
    """
    generator = ChartGenerator()

    if chart_type == 'line':
        # Generate sample time series data
        start_date = datetime(2024, 1, 1)
        data = []
        value = 10000
        for i in range(12):
            date = start_date + timedelta(days=i*30)
            value += random.uniform(-1000, 2000)
            data.append((date, value))

        return generator.generate_line_chart(
            data,
            title="Monthly Revenue Trend",
            ylabel="Revenue ($)"
        )

    elif chart_type == 'bar':
        categories = ['Q1', 'Q2', 'Q3', 'Q4']
        values = [random.uniform(50000, 100000) for _ in range(4)]

        return generator.generate_bar_chart(
            categories,
            values,
            title="Quarterly Performance"
        )

    elif chart_type == 'pie':
        labels = ['Product A', 'Product B', 'Product C', 'Product D']
        values = [random.uniform(10000, 50000) for _ in range(4)]

        return generator.generate_pie_chart(
            labels,
            values,
            title="Revenue by Product"
        )

    elif chart_type == 'dashboard':
        # Generate sample dashboard data
        start_date = datetime(2024, 1, 1)
        trend_dates = [start_date + timedelta(days=i*30) for i in range(12)]
        revenues = [10000 + i*1000 + random.uniform(-500, 500) for i in range(12)]

        metrics = {
            'trend_dates': trend_dates,
            'revenues': revenues,
            'expense_categories': ['Operating', 'Marketing', 'R&D', 'Admin'],
            'expense_values': [40000, 25000, 20000, 15000],
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'current_year': [120000, 135000, 145000, 160000, 155000, 170000],
            'previous_year': [100000, 115000, 125000, 140000, 135000, 150000],
            'kpis': {
                'Total Revenue': '$1.2M',
                'Net Profit': '$340K',
                'Growth Rate': '+23.5%',
                'Customer Count': '12,450'
            }
        }

        return generator.generate_financial_dashboard(metrics, width=width, height=height)

    return None
