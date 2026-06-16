import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

# Generate GIS dataset (same as before)
np.random.seed(42)
dates = pd.date_range('2025-01-01', periods=100, freq='D')
regions = np.random.choice(['Bangalore', 'Mumbai', 'Delhi', 'Chennai'], 100)
products = np.random.choice(['Hospitals', 'Parks', 'Schools', 'Roads'], 100)
quantity = np.random.randint(1, 100, 100)
price = np.random.uniform(10, 500, 100)
df = pd.DataFrame({
    'date': dates, 'region': regions, 'product': products, 
    'quantity': quantity, 'price': price
})
df['revenue'] = df['quantity'] * df['price']  # [code_file:7]

## 🛠️ REUSABLE DATA PROCESSING FUNCTIONS

def inspect_data(df: pd.DataFrame) -> Dict[str, str]:
    """Comprehensive data inspection with key metrics."""
    return {
        'shape': f"{df.shape[0]} rows × {df.shape[1]} cols",
        'memory': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
        'missing': df.isnull().sum().sum(),
        'dtypes': df.dtypes.value_counts().to_dict()
    }

def clean_data(df: pd.DataFrame, drop_missing: bool = True) -> pd.DataFrame:
    """Standard data cleaning pipeline."""
    df_clean = df.copy()
    # Handle missing values
    if drop_missing:
        df_clean = df_clean.dropna()
    # Fix data types
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    numeric_cols = df_clean.select_dtypes(include=['object']).columns.difference(['region', 'product'])
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    return df_clean

def filter_gis_data(df: pd.DataFrame, region: str = None, product: str = None, 
                   min_revenue: float = None) -> pd.DataFrame:
    """Flexible GIS data filtering by region, product, or revenue threshold."""
    filtered = df.copy()
    if region:
        filtered = filtered[filtered['region'] == region]
    if product:
        filtered = filtered[filtered['product'] == product]
    if min_revenue:
        filtered = filtered[filtered['revenue'] >= min_revenue]
    return filtered

def aggregate_metrics(df: pd.DataFrame, group_cols: List[str], 
                     value_col: str = 'revenue') -> pd.DataFrame:
    """Multi-level aggregation with custom metrics."""
    return df.groupby(group_cols)[value_col].agg([
        'sum', 'mean', 'count', ('top_5', lambda x: x.nlargest(5).sum())
    ]).round(2)

def create_pivot_table(df: pd.DataFrame, index: str, columns: str, 
                      values: str = 'revenue') -> pd.DataFrame:
    """Create pivot tables for cross-tab analysis."""
    return df.pivot_table(values=values, index=index, columns=columns, 
                         aggfunc='sum', fill_value=0).round(2)

def time_series_analysis(df: pd.DataFrame, date_col: str = 'date', 
                        period: str = 'M') -> pd.DataFrame:
    """Generate time-based aggregations."""
    df_ts = df.copy()
    df_ts[date_col] = pd.to_datetime(df_ts[date_col])
    df_ts['period'] = df_ts[date_col].dt.to_period(period)
    return df_ts.groupby('period')[['revenue', 'quantity']].sum()

# 💾 DATA VALIDATION FUNCTIONS
def validate_gis_data(df: pd.DataFrame) -> Dict[str, bool]:
    """Validate GIS dataset integrity."""
    issues = {}
    issues['valid_dates'] = df['date'].dtype == 'datetime64[ns]'
    issues['positive_quantities'] = (df['quantity'] > 0).all()
    issues['positive_prices'] = (df['price'] > 0).all()
    issues['revenue_consistent'] = np.allclose(df['revenue'], df['quantity'] * df['price'])
    return issues

## 🚀 MAIN PROCESSING PIPELINE
def process_gis_dataset(df_raw: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Complete GIS data processing pipeline."""
    print("🔍 Inspecting raw data...")
    print(inspect_data(df_raw))
    
    print("\n🧹 Cleaning data...")
    df_clean = clean_data(df_raw)
    
    print("\n✅ Data validation:", validate_gis_data(df_clean))
    
    print("\n📊 Processing analytics...")
    bangalore_hospitals = filter_gis_data(df_clean, 'Bangalore', 'Hospitals')
    
    results = {
        'cleaned': df_clean,
        'high_value': filter_gis_data(df_clean, min_revenue=20000),
        'summary': aggregate_metrics(df_clean, ['region', 'product']),
        'pivot': create_pivot_table(df_clean, 'region', 'product'),
        'monthly': time_series_analysis(df_clean),
        'bangalore_hospitals': bangalore_hospitals
    }
    
    # Export all results
    for key, df_result in results.items():
        df_result.to_csv(f'{key}.csv', index=True if 'pivot' in key else False)
    
    return results

## 📈 USAGE EXAMPLES
if __name__ == "__main__":
    # Run complete pipeline
    results = process_gis_dataset(df)
    
    # Selective processing
    print("\n🏥 Bangalore Hospitals:")
    print(filter_gis_data(df, 'Bangalore', 'Hospitals')[['date', 'revenue']])
    
    print("\n📊 Monthly Trends:")
    print(results['monthly'])
    
    print("\n💰 High-value contracts (>₹20K):")
    print(f"{len(results['high_value'])} records")  # [code_file:7]
