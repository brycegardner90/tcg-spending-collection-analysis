import pandas as pd

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv('/mnt/user-data/uploads/collectr_export_19-06-2026.csv')

# ── Data correction: Drowzee IR Holofoil (210/198) quantity 2 → 1 ─────────────
drowzee_mask = (
    (df['Product Name'] == 'Drowzee') &
    (df['Card Number'] == '210/198') &
    (df['Set'] == 'Scarlet & Violet Base Set')
)
df.loc[drowzee_mask, 'Quantity'] = 1

# ── Rename columns ────────────────────────────────────────────────────────────
mp_col = 'Market Price (As of 2026-06-19)'
df = df.rename(columns={
    'Portfolio Name':  'portfolio',
    'Category':        'category',
    'Set':             'set_name',
    'Product Name':    'card_name',
    'Card Number':     'card_number',
    'Rarity':          'rarity',
    'Variance':        'variance',
    'Grade':           'grade',
    'Card Condition':  'condition',
    'Average Cost Paid': 'avg_cost_paid',
    mp_col:            'market_price',
    'Price Override':  'price_override',
    'Watchlist':       'watchlist',
    'Date Added':      'date_added',
    'Notes':           'notes'
})

# ── Parse dates ───────────────────────────────────────────────────────────────
df['date_added'] = pd.to_datetime(df['date_added'])
df['year_added']       = df['date_added'].dt.year
df['month_added']      = df['date_added'].dt.month
df['month_name_added'] = df['date_added'].dt.strftime('%b')
df['year_month_added'] = df['date_added'].dt.to_period('M').astype(str)

# ── Derived value columns ─────────────────────────────────────────────────────
df['total_market_value'] = df['market_price'] * df['Quantity']

# High value flag (>= $50)
df['high_value_flag'] = df['market_price'] >= 50.0

# Rarity tier grouping for cleaner viz
rarity_tier = {
    'Common':                   'Common/Uncommon',
    'Uncommon':                 'Common/Uncommon',
    'Rare':                     'Rare',
    'Holo Rare':                'Rare',
    'Radiant Rare':             'Rare',
    'Amazing Rare':             'Rare',
    'Double Rare':              'Double Rare',
    'ACE SPEC Rare':            'ACE SPEC',
    'Illustration Rare':        'Illustration Rare',
    'Shiny Rare':               'Shiny Rare',
    'Shiny Holo Rare':          'Shiny Rare',
    'Ultra Rare':               'Ultra Rare',
    'Shiny Ultra Rare':         'Ultra Rare',
    'Special Illustration Rare':'Special Illustration Rare',
    'Hyper Rare':               'Hyper Rare',
    'Secret Rare':              'Secret Rare',
    'Promo':                    'Promo',
    'Classic Collection':       'Other',
}
df['rarity_tier'] = df['rarity'].map(rarity_tier).fillna('Other')

# ── Drop columns not needed for Tableau ──────────────────────────────────────
df = df.drop(columns=['portfolio', 'price_override', 'notes', 'avg_cost_paid'])

# ── Summary ───────────────────────────────────────────────────────────────────
print('Shape:', df.shape)
print()
print('Total cards (qty):', df['Quantity'].sum())
print('Total market value: $', df['total_market_value'].sum().round(2))
print()
print('By category:')
print(df.groupby('category').agg(
    cards=('Quantity','sum'),
    value=('total_market_value','sum')
).round(2))
print()
print('High value cards (>=$50):', df[df['high_value_flag']]['card_name'].count())
print('High value total: $', df[df['high_value_flag']]['total_market_value'].sum().round(2))
print()
print('Top 5 by value:')
print(df.nlargest(5, 'total_market_value')[['card_name','set_name','rarity','market_price','Quantity','total_market_value']].to_string())

# ── Export ────────────────────────────────────────────────────────────────────
output_path = '/mnt/user-data/outputs/collection_clean.csv'
df.to_csv(output_path, index=False)
print(f'\nExported to {output_path}')
