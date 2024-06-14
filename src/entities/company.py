import entities.income_statement as IncomeStatement

class Company:

  def __init__(self, name, ticker) -> None:
    self.name = name
    self.ticker = ticker
    self.income_statements = []

  def add_income_statement(self, income_statement: IncomeStatement):
    self.income_statements.append(income_statement)