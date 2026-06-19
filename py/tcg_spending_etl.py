import pandas as pd

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv('/mnt/user-data/uploads/Chase_TCG_Purchases.CSV')

# ── Clean ─────────────────────────────────────────────────────────────────────
# Parse dates
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
df['Post Date'] = pd.to_datetime(df['Post Date'])

# Flip sales to positive; returns are already positive from Chase
# Sales come in as negative (charges), returns as positive (credits)
df['Amount'] = df['Amount'].abs()

# Drop Memo (empty) and Description/Category (all same value)
df = df.drop(columns=['Memo', 'Description', 'Category'])

# Rename for Tableau friendliness
df = df.rename(columns={
    'Transaction Date': 'transaction_date',
    'Post Date':        'post_date',
    'Type':             'transaction_type',
    'Amount':           'amount'
})

# ── Derived columns ───────────────────────────────────────────────────────────
df['year']       = df['transaction_date'].dt.year
df['month']      = df['transaction_date'].dt.month
df['month_name'] = df['transaction_date'].dt.strftime('%b')
df['year_month'] = df['transaction_date'].dt.to_period('M').astype(str)  # e.g. 2024-05

# Net amount: sales positive, returns negative (useful for net spend calcs in Tableau)
df['net_amount'] = df.apply(
    lambda r: r['amount'] if r['transaction_type'] == 'Sale' else -r['amount'],
    axis=1
)

# ── Summary check ─────────────────────────────────────────────────────────────
print("Shape:", df.shape)
print("\nSample:")
print(df.head(10).to_string())
print("\nType breakdown:")
print(df.groupby('transaction_type')['amount'].agg(['count', 'sum']).round(2))
print("\nTotal gross spend (sales only): $", df[df['transaction_type'] == 'Sale']['amount'].sum().round(2))
print("Total returns:                  $", df[df['transaction_type'] == 'Return']['amount'].sum().round(2))
print("Net spend:                      $", df['net_amount'].sum().round(2))

# ── Export ────────────────────────────────────────────────────────────────────
output_path = '/mnt/user-data/outputs/tcg_spending_clean.csv'
df.to_csv(output_path, index=False)
print(f"\nExported to {output_path}")
