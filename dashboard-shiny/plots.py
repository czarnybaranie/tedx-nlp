import pandas as pd
import plotly.express as px

# import datetime as dt
# Basic plots

def line_plot_videos_views(df, selected_var):
    if selected_var == "All categories" or selected_var is None:
        videos_count = df.groupby("year").size()
        avg_views = df.groupby("year")['views'].mean()
    else:
        videos_cat = df[df['category'] == selected_var]
        videos_count = videos_cat.groupby("year").size()
        avg_views = videos_cat.groupby("year")['views'].mean()
    
    fig = px.bar(videos_count, x=videos_count.index, y=videos_count.values, labels={'y': 'Count'}, title='Videos Count and Average Views per Year')
    fig.add_scatter(x=avg_views.index, y=avg_views.values, mode='lines+markers', name='Average Views', yaxis='y2', line=dict(color='firebrick', width=2), marker=dict(size=8), showlegend=False)
    
    fig.update_layout(
        yaxis=dict(
            title='Number of Videos',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title='Average Views',
            titlefont=dict(color='firebrick'),
            tickfont=dict(color='firebrick'),
            overlaying='y',
            side='right'
        ),
        xaxis=dict(
            title='Year',
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            dtick=1  # Show every year on the x-axis

        ),
        title=dict(
            text=f"Videos Count and Average Views per Year for: {selected_var}",
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    
    return fig



def treemap_languages_plot(df, selected_var):
    if selected_var == "All categories" or selected_var is None:
        value_counts = df['language'].value_counts()
    else:
        value_counts = df[df['category'] == selected_var]['language'].value_counts()
    
    total_count = value_counts.sum()
    percentages = (value_counts / total_count * 100).round(2)
    
    fig_treemap = px.treemap(
        names=value_counts.index,
        parents=['All'] * len(value_counts),
        values=value_counts.values,
        title='Treemap of Languages',
        custom_data=[percentages]
    )
    
    fig_treemap.update_traces(texttemplate='<b>%{label}</b><br>%{customdata[0]}%')
    fig_treemap.update_layout(
        title=dict(
            text='Treemap of Languages',
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    return fig_treemap

# Categories

import pandas as pd
import plotly.express as px

from wordcloud import WordCloud
import matplotlib.pyplot as plt

def get_sunburst_mapping():
    sunburst_mapping = {
        "Human Experience": {
            "Personal Growth": ["personal growth", "mental health", "psychology"],
            "Health & Well-being": ["health", "nature"],
            "Creativity & Arts": ["creativity", "art", "music", "design", "entertainment"],
            "Culture & Society": ["culture", "gender", "social change", "history", "storytelling"]
        },
        "Knowledge & Education": {
            "Literature & Communication": ["literature", "storytelling", "communication"],
            "Education & Learning": ["education", "innovation", "technology"]
        },
        "Global Issues": {
            "Environment & Sustainability": ["environment", "climate change", "sustainability"],
            "Politics & Society": ["politics", "social change", "global issues", "humanity"],
            "Economics & Work": ["economics", "business", "work"]
        },
        "Science & Technology": {
            "Science & Exploration": ["science", "technology", "AI", "innovation"],
            "Global Challenges": ["climate change", "sustainability", "global issues"]
        },
        "Lifestyle & Leisure": {
            "Food & Entertainment": ["food", "entertainment", "design"],
            "Leisure & Creativity": ["music"]  # Focused on music as part of leisure
        }
    }
    return sunburst_mapping

def get_parent_categories():
    sunburst_mapping = get_sunburst_mapping()
    parent_categories = set()

    for grandparent, subcategories in sunburst_mapping.items():
        for parent in subcategories.keys():
            parent_categories.add(parent)

    return list(parent_categories)

def sunburst(df):
    # Define the hierarchy for the sunburst diagram
    sunburst_mapping = get_sunburst_mapping()

    # Flatten the hierarchy to create a parent mapping
    parent_mapping = {}
    for grandparent, subcategories in sunburst_mapping.items():
        for parent, children in subcategories.items():
            for child in children:
                parent_mapping[child] = parent
            parent_mapping[parent] = grandparent

    data = df.copy()

    # Add parent and root columns to the data
    root = 'All Categories'
    data['parent'] = data['category'].map(parent_mapping).fillna(root)
    data['root'] = data['parent'].map(parent_mapping).fillna(root)

    # Calculate percentage occurrence
    data_count = data.groupby(['category']).size().reset_index(name='count')
    data = data.merge(data_count, on='category')
    data['percentage'] = (data['count'] / data['count'].sum()) * 100

    # Create a sunburst chart
    fig = px.sunburst(
        data,
        path=['root', 'parent', 'category'],
        values='percentage',
        title='Sunburst Diagram of Categories',
    )

    # Update layout to place labels outside
    fig.update_traces(insidetextorientation='radial')

    fig.update_layout(
        title=dict(
            # text='Sunburst Diagram of Categories',
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
        # width=800,  # Set the width of the plot
        # height=800,  # Set the height of the plot
        # margin=dict(t=0, l=200, r=200, b=0),  # Adjust margins to center the plot
        # uniformtext=dict(minsize=10, mode='hide')
    )

    return fig

def sunburst_df(df):
    sunburst_mapping = get_sunburst_mapping()
    # Convert the hierarchy to a DataFrame
    rows = []
    for grandparent, subcategories in sunburst_mapping.items():
        for parent, children in subcategories.items():
            for child in children:
                rows.append([grandparent, parent, child])

    hierarchy_df = pd.DataFrame(rows, columns=['Grandparent', 'Parent', 'Child'])
    data_count = df.groupby(['category']).size().reset_index(name='count')
    total_count = data_count['count'].sum()
    hierarchy_df = pd.merge(hierarchy_df, data_count, how='left', left_on='Child', right_on='category')
    hierarchy_df['count'] = hierarchy_df['count'].fillna(0)
    hierarchy_df['percentage'] = round((hierarchy_df['count'] / total_count) * 100,2)
    hierarchy_df.drop(columns=['category'], inplace=True)
    return hierarchy_df
    # # Merge with the original df based on the 'Child' column
    # merged_df = pd.merge(hierarchy_df, df, left_on='Child', right_on='category', how='left')
    # return merged_df

# def stacked_plot_category(df):
#     # 10. Category Popularity over Time
#     plt.figure(figsize=(12, 8))
#     category_time = df.groupby(['year', 'category'])['views'].sum().unstack().fillna(0)
#     category_time.plot(kind='area', stacked=True, figsize=(12, 8), colormap='tab10')
#     plt.title('Category Popularity Over Time')
#     plt.xlabel('Year')
#     plt.ylabel('Total Views')
#     plt.legend(title='Category', bbox_to_anchor=(1, 1))
#     plt.show()

def category_popularity_over_time(df, selected_category=None):
    # Group data by year and category, summing the views
    category_time = df.groupby(['year', 'category'])['views'].sum().reset_index()

    # Create an area plot using Plotly Express
    fig = px.area(
        category_time,
        x='year',
        y='views',
        color='category',
        labels={'views': 'Total Views', 'year': 'Year'},
        color_discrete_sequence=px.colors.qualitative.Alphabet  # Use a different color sequence
    )

    # Update traces to remove boundary lines
    fig.update_traces(line=dict(width=0))

    # Highlight the selected category
    if selected_category and selected_category != 'All categories':
        fig.update_traces(
            selector=dict(name=selected_category),
            line=dict(width=2, color='black')
        )

    # Update layout for better visualization
    fig.update_layout(
        title=dict(
            text='Category Popularity Over Time',
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
        xaxis_title='Year',
        yaxis_title='Total Views',
        legend_title='Category',
        legend=dict(x=1, y=1),
        height=600,  # Increase the height of the chart
        # plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(dtick=1)  # Set dtick to 1 for the x-axis
    )

    return fig

# Wordcloud

# # This sadly does not work in the current environment, as matplotlib is not supported

# def wordcloud_plot(df, selected_var):
#     if selected_var == "All categories" or selected_var is None:
#         data = df.copy()
#     else:
#         data = df[df['category'] == selected_var]
    
#     wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(data['translated_title'].dropna()))
#     plt.figure(figsize=(10, 5))
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.axis('off')
#     return plt

# Sentiment


def sentiment_analysis_plot(df,selected_var):
    if selected_var == "All categories" or selected_var is None:
        df = df
        title_var = 'Sentiment Percentage per Year'
    else:
        df = df[df['category'] == selected_var]
        title_var = f'Sentiment Percentage per Year for {selected_var}'
    # Normalize the counts to percentages
    sentiment_counts = df.groupby(['year', 'sentiment']).size().unstack()

    sentiment_percentages = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100

    # Reset index to use 'year' as a column
    sentiment_percentages = sentiment_percentages.reset_index()

    # Melt the DataFrame to long format
    sentiment_percentages_melted = sentiment_percentages.melt(id_vars='year', var_name='sentiment', value_name='percentage')

    # Define vibrant colors
    colors = ['#FF6347', '#FFD700', '#32CD32']

    # Plot the result
    fig = px.bar(sentiment_percentages_melted, x='year', y='percentage', color='sentiment', 
                labels={'year': 'Year', 'percentage': 'Percentage'},
                color_discrete_sequence=colors
                )
    fig.update_layout(
        title = dict(
            text = title_var,
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold',
        ),
        height=600,  # Increase the height of the chart
        xaxis=dict(dtick=1),  # Set dtick to 1 for the x-axis
    )
    return fig

# Views

# def log_scale_boxplot_by_categories(df, selected_categories=None):
#     """
#     selected_categories is a list of category names from the df 
#     that the user selected in a multiple choice input.
#     """

#     data = df.copy()
#     if selected_categories:
#         data = data[data['category'].isin(selected_categories)]
#     else:
#         data = data[data['category'].notnull()]
#     data = data.dropna(subset=['views'])  # Remove missing values
#     data = data[data['views'] > 0]  # Remove zero or negative views

#     fig = px.box(data, x='category', y='views', title='Log-Scale Views by Selected Categories')
#     fig.update_yaxes(type="log")
#     return fig

def log_scale_boxplot_by_categories(df, start_date, end_date, selected_categories=None, selected_lang='All Languages'):
    """
    selected_categories is a list of parent category names from the df 
    that the user selected in a multiple choice input.
    """

    sunburst_mapping = get_sunburst_mapping()

    # Flatten the hierarchy to map each category to its parent
    parent_map = {}
    for grandparent, subcategories in sunburst_mapping.items():
        for parent, children in subcategories.items():
            for child in children:
                parent_map[child] = parent
            parent_map[parent] = parent

    data = df.copy()
    data['parent'] = data['category'].map(parent_map).dropna()

    # Category filter
    if selected_categories:
        data = data[data['parent'].isin(selected_categories)]
    else:
        data = data[data['parent'].notnull()]

    # Language filter
    if selected_lang == 'All Languages':
        data = data
    else:
        data = data[data['language'] == selected_lang]

    # Year filter
    data['year'] = pd.to_numeric(data['year'], errors='coerce')
    data = data[(data['year'] >= start_date) & (data['year'] <= end_date)]

    data = data.dropna(subset=['views'])  # Remove missing values
    data = data[data['views'] > 0]  # Remove zero or negative views

    fig = px.box(data, x='parent', y='views', title='Log-Scale Views by Selected Parent Categories')
    fig.update_yaxes(type="log")
    fig.update_layout(
        title=dict(
            text='Log-Scale Views by Selected Parent Categories',
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
        xaxis_title='Category',
        yaxis_title='Views (Log-Scale)',
        height=600,  # Increase the height of the chart
        xaxis=dict(dtick=1),  # Set dtick to 1 for the x-axis
    )
    return fig

def views_vs_title_length_plot(df, start_date, end_date, selected_categories=None, selected_lang='All Languages'):
    """
    Creates a scatter plot showing the correlation between title length 
    and the number of views, with sentiment as colors, for the selected filters.
    """
    sunburst_mapping = get_sunburst_mapping()

    # Flatten the hierarchy to map each category to its parent
    parent_map = {}
    for grandparent, subcategories in sunburst_mapping.items():
        for parent, children in subcategories.items():
            for child in children:
                parent_map[child] = parent
            parent_map[parent] = parent

    data = df.copy()
    data['parent'] = data['category'].map(parent_map).dropna()

    # Category filter
    if selected_categories:
        data = data[data['parent'].isin(selected_categories)]
    else:
        data = data[data['parent'].notnull()]
        op = 0.05

    # Language filter
    op = 0.05 # default opacity
    if selected_lang != 'All Languages' and selected_lang is not None:
        data = data[data['language'] == selected_lang]
        if selected_lang != 'en':
            op = 1 # Change the alpha value for transparency for clearer visualization

    # Year filter
    data['year'] = pd.to_numeric(data['year'], errors='coerce')
    data = data[(data['year'] >= start_date) & (data['year'] <= end_date)]

    # Remove missing or non-positive views
    data = data.dropna(subset=['views'])  
    data = data[data['views'] > 0]

    # Calculate title length
    data['title_length'] = data['title'].apply(lambda x: len(str(x)))

    # Ensure sentiment column is present
    data = data.dropna(subset=['sentiment'])


    # Remove the specific point with title length of 116, as this is most likely and error
    data = data[data['title_length'] != 116]

    # Define custom color mapping
    color_map = {
    'Positive': 'green',
    'Neutral': 'gray',
    'Negative': 'red'
    }

    # Create a scatter plot with low alpha
    fig = px.scatter(
        data,
        x='title_length',
        y='views',
        color='sentiment',
        title='Views vs Title Length with Sentiment as Colors',
        opacity=op,  # Set the alpha value for transparency,
        color_discrete_map=color_map
    )
    fig.update_yaxes(type="log")
    # fig.update_xaxes(range=[0, 100])  # Set the x-axis range
    fig.update_layout(
        xaxis_title='Title Length',
        yaxis_title='Views (Log-Scale)',
        height=600,
        title=dict(
            text='Views vs Title Length with Sentiment as Colors',
            font=dict(size=20),
            x=0.5,  # Center the title
            xanchor='center',
            font_weight='bold'
        ),
    )
    return fig