"""
DATA ANALYTICS INTERNSHIP - TASK 5: INTERACTIVE DASHBOARD DESIGN
Professional Sales & Financial Dashboard
Objective: Create interactive business dashboard for data-driven decision 
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .dashboard-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stSelectbox > div > div > select {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA GENERATION FUNCTION
# =============================================================================

@st.cache_data
def load_sales_data():
    """Generate comprehensive sales dataset for dashboard"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Define parameters
    n_records = 5000
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 8, 31)
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Product categories and products
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Health & Beauty']
    products = {
        'Electronics': ['Smartphone', 'Laptop', 'Tablet', 'Headphones', 'Smart Watch'],
        'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes'],
        'Home & Garden': ['Furniture', 'Kitchen Appliance', 'Garden Tools', 'Home Decor', 'Lighting'],
        'Sports': ['Running Shoes', 'Gym Equipment', 'Sports Apparel', 'Outdoor Gear', 'Fitness Tracker'],
        'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Children Books', 'E-Books'],
        'Health & Beauty': ['Skincare', 'Makeup', 'Supplements', 'Personal Care', 'Fragrances']
    }
    
    # Regions and sales reps
    regions = ['North', 'South', 'East', 'West', 'Central']
    sales_reps = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Brown', 'Eva Wilson',
                  'Frank Miller', 'Grace Lee', 'Henry Taylor', 'Iris Chen', 'Jack Wilson']
    
    # Customer segments
    segments = ['Enterprise', 'Small Business', 'Individual']
    
    # Generate synthetic data
    records = []
    
    for i in range(n_records):
        # Random date with seasonal patterns
        date = np.random.choice(date_range)
        month = date.month
        
        # Seasonal multiplier
        seasonal_multiplier = 1.0
        if month in [11, 12]:  # Holiday season
            seasonal_multiplier = 1.4
        elif month in [6, 7, 8]:  # Summer
            seasonal_multiplier = 1.2
        elif month in [1, 2]:  # Post-holiday
            seasonal_multiplier = 0.8
        
        # Select category and product
        category = np.random.choice(categories)
        product = np.random.choice(products[category])
        
        # Generate sales data with realistic patterns
        base_price = {
            'Electronics': np.random.normal(300, 100),
            'Clothing': np.random.normal(50, 20),
            'Home & Garden': np.random.normal(150, 50),
            'Sports': np.random.normal(80, 30),
            'Books': np.random.normal(25, 10),
            'Health & Beauty': np.random.normal(40, 15)
        }[category]
        
        unit_price = max(10, base_price * seasonal_multiplier)
        quantity = np.random.randint(1, 10)
        gross_sales = unit_price * quantity
        
        # Calculate costs and profit
        cost_rate = np.random.uniform(0.4, 0.7)
        cost = gross_sales * cost_rate
        profit = gross_sales - cost
        discount = np.random.uniform(0, 0.15) if np.random.random() > 0.7 else 0
        net_sales = gross_sales * (1 - discount)
        
        # Customer and order details
        customer_id = f"CUST_{np.random.randint(1000, 9999)}"
        order_id = f"ORD_{i+1:05d}"
        
        record = {
            'Order_ID': order_id,
            'Date': date,
            'Year': date.year,
            'Month': date.month,
            'Month_Name': date.strftime('%B'),
            'Quarter': f"Q{(date.month-1)//3 + 1}",
            'Day_of_Week': date.strftime('%A'),
            'Customer_ID': customer_id,
            'Customer_Segment': np.random.choice(segments, p=[0.3, 0.4, 0.3]),
            'Product_Category': category,
            'Product_Name': product,
            'Region': np.random.choice(regions),
            'Sales_Rep': np.random.choice(sales_reps),
            'Unit_Price': round(unit_price, 2),
            'Quantity': quantity,
            'Gross_Sales': round(gross_sales, 2),
            'Discount': round(discount, 3),
            'Net_Sales': round(net_sales, 2),
            'Cost': round(cost, 2),
            'Profit': round(profit, 2),
            'Profit_Margin': round((profit / gross_sales) * 100, 2)
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Add some calculated fields
    df['Sales_Target'] = df['Net_Sales'] * np.random.uniform(0.8, 1.2, len(df))
    df['Target_Achievement'] = (df['Net_Sales'] / df['Sales_Target']) * 100
    df['Customer_Lifetime_Value'] = df.groupby('Customer_ID')['Net_Sales'].transform('sum')
    
    return df

# =============================================================================
# DASHBOARD FUNCTIONS
# =============================================================================

def create_kpi_metrics(df, filtered_df):
    """Create KPI metrics cards"""
    
    # Current period metrics
    total_sales = filtered_df['Net_Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    avg_profit_margin = filtered_df['Profit_Margin'].mean()
    total_orders = len(filtered_df)
    avg_order_value = filtered_df['Net_Sales'].mean()
    unique_customers = filtered_df['Customer_ID'].nunique()
    
    # Previous period comparison (for growth calculation)
    if len(filtered_df) > 0:
        min_date = filtered_df['Date'].min()
        max_date = filtered_df['Date'].max()
        period_days = (max_date - min_date).days
        
        if period_days > 30:  # If more than 30 days, compare with previous period
            prev_start = min_date - timedelta(days=period_days)
            prev_end = min_date
            prev_df = df[(df['Date'] >= prev_start) & (df['Date'] < prev_end)]
            
            prev_sales = prev_df['Net_Sales'].sum() if len(prev_df) > 0 else 1
            sales_growth = ((total_sales - prev_sales) / prev_sales) * 100 if prev_sales > 0 else 0
        else:
            sales_growth = 0
    else:
        sales_growth = 0
    
    return {
        'total_sales': total_sales,
        'total_profit': total_profit,
        'avg_profit_margin': avg_profit_margin,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'unique_customers': unique_customers,
        'sales_growth': sales_growth
    }

def create_time_series_chart(df):
    """Create time series sales chart"""
    
    # Group by date for time series
    daily_sales = df.groupby('Date').agg({
        'Net_Sales': 'sum',
        'Profit': 'sum',
        'Order_ID': 'count'
    }).reset_index()
    daily_sales.columns = ['Date', 'Net_Sales', 'Profit', 'Orders']
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['Daily Sales Trend', 'Daily Orders Count'],
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Sales trend
    fig.add_trace(
        go.Scatter(
            x=daily_sales['Date'],
            y=daily_sales['Net_Sales'],
            mode='lines',
            name='Net Sales',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>Sales:</b> $%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Orders count
    fig.add_trace(
        go.Scatter(
            x=daily_sales['Date'],
            y=daily_sales['Orders'],
            mode='lines',
            name='Orders',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>Orders:</b> %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        title_text="Sales Performance Over Time",
        title_x=0.5,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

def create_category_analysis(df):
    """Create category performance analysis"""
    
    # Group by category
    category_metrics = df.groupby('Product_Category').agg({
        'Net_Sales': 'sum',
        'Profit': 'sum',
        'Order_ID': 'count',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    category_metrics.columns = ['Category', 'Net_Sales', 'Profit', 'Orders', 'Avg_Profit_Margin']
    category_metrics = category_metrics.sort_values('Net_Sales', ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            y=category_metrics['Category'],
            x=category_metrics['Net_Sales'],
            orientation='h',
            name='Net Sales',
            marker_color='lightblue',
            hovertemplate='<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title="Sales by Product Category",
        title_x=0.5,
        xaxis_title="Net Sales ($)",
        yaxis_title="Product Category",
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_regional_performance(df):
    """Create regional performance analysis"""
    
    # Group by region
    regional_metrics = df.groupby('Region').agg({
        'Net_Sales': 'sum',
        'Profit': 'sum',
        'Order_ID': 'count',
        'Customer_ID': 'nunique'
    }).reset_index()
    
    regional_metrics.columns = ['Region', 'Net_Sales', 'Profit', 'Orders', 'Customers']
    
    # Create pie chart for sales distribution
    fig = px.pie(
        regional_metrics,
        values='Net_Sales',
        names='Region',
        title='Sales Distribution by Region',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data=['Orders', 'Customers']
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Orders: %{customdata[0]}<br>Customers: %{customdata[1]}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        template='plotly_white'
    )
    
    return fig

def create_sales_rep_performance(df):
    """Create sales rep performance analysis"""
    
    # Group by sales rep
    rep_metrics = df.groupby('Sales_Rep').agg({
        'Net_Sales': 'sum',
        'Profit': 'sum',
        'Order_ID': 'count',
        'Customer_ID': 'nunique',
        'Target_Achievement': 'mean'
    }).reset_index()
    
    rep_metrics.columns = ['Sales_Rep', 'Net_Sales', 'Profit', 'Orders', 'Customers', 'Avg_Target_Achievement']
    rep_metrics = rep_metrics.sort_values('Net_Sales', ascending=False).head(10)
    
    # Create bar chart
    fig = px.bar(
        rep_metrics,
        x='Sales_Rep',
        y='Net_Sales',
        title='Top 10 Sales Representatives Performance',
        color='Avg_Target_Achievement',
        color_continuous_scale='RdYlGn',
        hover_data=['Profit', 'Orders', 'Customers']
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        xaxis_title="Sales Representative",
        yaxis_title="Net Sales ($)",
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    
    return fig

def create_customer_analysis(df):
    """Create customer segment analysis"""
    
    # Group by customer segment
    segment_metrics = df.groupby('Customer_Segment').agg({
        'Net_Sales': 'sum',
        'Profit': 'sum',
        'Order_ID': 'count',
        'Customer_ID': 'nunique',
        'Customer_Lifetime_Value': 'mean'
    }).reset_index()
    
    segment_metrics.columns = ['Segment', 'Net_Sales', 'Profit', 'Orders', 'Customers', 'Avg_CLV']
    
    # Create subplot with multiple metrics
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Revenue by Segment', 'Customer Count by Segment'],
        specs=[[{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Revenue bar chart
    fig.add_trace(
        go.Bar(
            x=segment_metrics['Segment'],
            y=segment_metrics['Net_Sales'],
            name='Revenue',
            marker_color='lightcoral',
            hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Customer count pie chart
    fig.add_trace(
        go.Pie(
            labels=segment_metrics['Segment'],
            values=segment_metrics['Customers'],
            name='Customers',
            hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Percentage: %{percent}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="Customer Segment Analysis",
        title_x=0.5,
        template='plotly_white'
    )
    
    return fig

def create_profitability_analysis(df):
    """Create profitability analysis chart"""
    
    # Create scatter plot of sales vs profit
    fig = px.scatter(
        df,
        x='Net_Sales',
        y='Profit',
        color='Product_Category',
        size='Quantity',
        hover_data=['Product_Name', 'Region', 'Profit_Margin'],
        title='Sales vs Profit Analysis'
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5,
        xaxis_title="Net Sales ($)",
        yaxis_title="Profit ($)",
        template='plotly_white'
    )
    
    return fig

# =============================================================================
# MAIN DASHBOARD LAYOUT
# =============================================================================

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🏢 Sales Performance Dashboard</h1>
        <p>Interactive Business Intelligence Dashboard for Data-Driven Decision Making</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading sales data...'):
        df = load_sales_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Dashboard Filters")
    st.sidebar.markdown("---")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min(),
        max_value=df['Date'].max()
    )
    
    # Region filter
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "Select Region(s)",
        options=regions,
        default=['All']
    )
    
    # Product Category filter
    categories = ['All'] + sorted(df['Product_Category'].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Select Product Category",
        options=categories,
        default=['All']
    )
    
    # Customer Segment filter
    segments = ['All'] + sorted(df['Customer_Segment'].unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "Select Customer Segment",
        options=segments,
        default=['All']
    )
    
    # Sales Rep filter
    reps = ['All'] + sorted(df['Sales_Rep'].unique().tolist())
    selected_reps = st.sidebar.selectbox(
        "Select Sales Representative",
        options=reps
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.Timestamp(start_date)) &
            (filtered_df['Date'] <= pd.Timestamp(end_date))
        ]
    
    # Region filter
    if 'All' not in selected_regions and len(selected_regions) > 0:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    
    # Category filter
    if 'All' not in selected_categories and len(selected_categories) > 0:
        filtered_df = filtered_df[filtered_df['Product_Category'].isin(selected_categories)]
    
    # Segment filter
    if 'All' not in selected_segments and len(selected_segments) > 0:
        filtered_df = filtered_df[filtered_df['Customer_Segment'].isin(selected_segments)]
    
    # Sales Rep filter
    if selected_reps != 'All':
        filtered_df = filtered_df[filtered_df['Sales_Rep'] == selected_reps]
    
    # Display filter summary
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Filtered Records:** {len(filtered_df):,}")
    st.sidebar.write(f"**Total Records:** {len(df):,}")
    
    # Main dashboard content
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
        return
    
    # KPI Metrics Row
    st.markdown("## 📊 Key Performance Indicators")
    kpi_metrics = create_kpi_metrics(df, filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Sales",
            value=f"${kpi_metrics['total_sales']:,.0f}",
            delta=f"{kpi_metrics['sales_growth']:+.1f}%" if kpi_metrics['sales_growth'] != 0 else None
        )
        
    with col2:
        st.metric(
            label="💵 Total Profit",
            value=f"${kpi_metrics['total_profit']:,.0f}"
        )
        
    with col3:
        st.metric(
            label="📈 Profit Margin",
            value=f"{kpi_metrics['avg_profit_margin']:.1f}%"
        )
        
    with col4:
        st.metric(
            label="📋 Total Orders",
            value=f"{kpi_metrics['total_orders']:,}"
        )
    
    # Second row of KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="🛒 Avg Order Value",
            value=f"${kpi_metrics['avg_order_value']:.0f}"
        )
        
    with col6:
        st.metric(
            label="👥 Unique Customers",
            value=f"{kpi_metrics['unique_customers']:,}"
        )
        
    with col7:
        st.metric(
            label="🎯 Revenue per Customer",
            value=f"${kpi_metrics['total_sales']/kpi_metrics['unique_customers']:.0f}"
        )
        
    with col8:
        st.metric(
            label="📦 Orders per Customer",
            value=f"{kpi_metrics['total_orders']/kpi_metrics['unique_customers']:.1f}"
        )
    
    # Charts Row 1
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_time_series_chart(filtered_df), use_container_width=True)
        
    with col2:
        st.plotly_chart(create_regional_performance(filtered_df), use_container_width=True)
    
    # Charts Row 2
    col3, col4 = st.columns(2)
    
    with col3:
        st.plotly_chart(create_category_analysis(filtered_df), use_container_width=True)
        
    with col4:
        st.plotly_chart(create_customer_analysis(filtered_df), use_container_width=True)
    
    # Charts Row 3
    st.plotly_chart(create_sales_rep_performance(filtered_df), use_container_width=True)
    
    # Profitability Analysis
    st.plotly_chart(create_profitability_analysis(filtered_df), use_container_width=True)
    
    # Data Table
    st.markdown("---")
    st.markdown("## 📋 Detailed Data View")
    
    # Show summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top 10 Products by Sales")
        top_products = filtered_df.groupby('Product_Name')['Net_Sales'].sum().sort_values(ascending=False).head(10)
        st.dataframe(top_products.reset_index())
    
    with col2:
        st.markdown("### Top 10 Customers by Revenue")
        top_customers = filtered_df.groupby('Customer_ID')['Net_Sales'].sum().sort_values(ascending=False).head(10)
        st.dataframe(top_customers.reset_index())
    
    # Raw data view
    with st.expander("🔍 View Raw Data"):
        st.dataframe(
            filtered_df[['Date', 'Order_ID', 'Customer_Segment', 'Product_Category', 
                        'Product_Name', 'Region', 'Sales_Rep', 'Net_Sales', 'Profit', 'Profit_Margin']],
            use_container_width=True
        )
    
    # Download functionality
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"sales_data_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
        📊 Sales Performance Dashboard | Data Analytics Internship - Task 5<br>
        Built with Streamlit & Plotly | © 2025 Skillytixs Analytics
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    main()