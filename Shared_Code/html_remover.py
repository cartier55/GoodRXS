import pandas as pd
import re

def remove_html_tags(df, column_name):
    # Regular expression pattern to match and remove HTML tags
    tag_re = re.compile(r'<[^>]+>')
    
    # Apply the regular expression to the specified column
    df[column_name] = df[column_name].apply(lambda x: tag_re.sub('', str(x)) if pd.notnull(x) else x)
    
    return df


df = pd.read_csv('./results/drug_info/all_drug_infos_complete.csv')
remove_html_tags(df, 'description')
print(df['description'].head())
df.to_csv('./results/drug_info/all_drug_infos_complete.csv', index=False)