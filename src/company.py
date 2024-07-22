class Company:

  def __init__(self, name, ticker) -> None:
    self.name = name
    self.ticker = ticker
    self.income_statements = {}
    self.balance_sheets = {}
  
  def __str__(self):
    return f"Company(name={self.name}, ticker={self.ticker})"