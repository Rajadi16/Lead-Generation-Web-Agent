"""
Export leads from database to Excel format for demo submission
"""
import pandas as pd
from sqlalchemy import create_engine
from database import Lead
import json

def export_leads_to_excel(output_file='lead_generation_output.xlsx'):
    """Export all leads to Excel with proper formatting"""
    
    # Connect to database
    engine = create_engine('sqlite:///leads.db')
    
    # Query all leads
    query = """
    SELECT 
        name,
        title,
        company,
        person_location,
        email,
        role_fit_score,
        company_intent_score,
        technographic_score,
        location_score,
        scientific_intent_score,
        total_score,
        recent_publication_count,
        data_source,
        created_at
    FROM leads
    ORDER BY total_score DESC
    """
    
    df = pd.read_sql(query, engine)
    
    # Calculate score category
    def get_category(score):
        if score >= 80:
            return 'Hot Lead'
        elif score >= 50:
            return 'Warm Lead'
        else:
            return 'Cold Lead'
    
    df['score_category'] = df['total_score'].apply(get_category)
    
    # Round scores to 1 decimal place
    score_columns = [
        'role_fit_score', 'company_intent_score', 'technographic_score',
        'location_score', 'scientific_intent_score', 'total_score'
    ]
    for col in score_columns:
        df[col] = df[col].round(1)
    
    # Rename columns for better readability
    df = df.rename(columns={
        'name': 'Name',
        'title': 'Job Title',
        'company': 'Company',
        'person_location': 'Location',
        'email': 'Email',
        'role_fit_score': 'Role Fit Score (0-30)',
        'company_intent_score': 'Company Intent Score (0-20)',
        'technographic_score': 'Technographic Score (0-25)',
        'location_score': 'Location Score (0-10)',
        'scientific_intent_score': 'Scientific Intent Score (0-40)',
        'total_score': 'Total Score (0-100)',
        'score_category': 'Category',
        'recent_publication_count': 'Publications',
        'data_source': 'Data Source',
        'created_at': 'Date Added'
    })
    
    # Create Excel writer with formatting
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Leads', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Leads']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        hot_format = workbook.add_format({'bg_color': '#C6EFCE'})  # Green
        warm_format = workbook.add_format({'bg_color': '#FFEB9C'})  # Yellow
        cold_format = workbook.add_format({'bg_color': '#FFC7CE'})  # Red
        
        # Format header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 25)  # Name
        worksheet.set_column('B:B', 30)  # Job Title
        worksheet.set_column('C:C', 35)  # Company
        worksheet.set_column('D:D', 25)  # Location
        worksheet.set_column('E:E', 35)  # Email
        worksheet.set_column('F:K', 15)  # Score columns
        worksheet.set_column('L:L', 12)  # Category
        worksheet.set_column('M:M', 12)  # Publications
        worksheet.set_column('N:N', 15)  # Data Source
        worksheet.set_column('O:O', 20)  # Date Added
        
        # Apply conditional formatting to Category column
        category_col = df.columns.get_loc('Category')
        for row_num in range(1, len(df) + 1):
            category = df.iloc[row_num - 1]['Category']
            if category == 'Hot Lead':
                worksheet.write(row_num, category_col, category, hot_format)
            elif category == 'Warm Lead':
                worksheet.write(row_num, category_col, category, warm_format)
            else:
                worksheet.write(row_num, category_col, category, cold_format)
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
    
    print(f"✅ Exported {len(df)} leads to {output_file}")
    print(f"\nBreakdown:")
    print(f"  - Hot Leads (80-100): {len(df[df['Category'] == 'Hot Lead'])}")
    print(f"  - Warm Leads (50-79): {len(df[df['Category'] == 'Warm Lead'])}")
    print(f"  - Cold Leads (0-49): {len(df[df['Category'] == 'Cold Lead'])}")
    
    return output_file

if __name__ == "__main__":
    export_leads_to_excel()
