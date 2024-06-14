import entities.company as Company

class IncomeStatement:

  def __init__(self, company: Company, year) -> None:
    self.company = company
    self.year = year
  
  def set_revenue(self, revenue):
    self.revenue = revenue
  
  def set_cost_of_goods_sold(self, cost_of_goods_sold):
    self.cost_of_goods_sold = cost_of_goods_sold

  def set_gross_profit(self, gross_profit):
    self.gross_profit = gross_profit
  
  def set_research_and_development_expenses(self, research_and_development_expenses):
    self.research_and_development_expenses = research_and_development_expenses
  
  def set_sgna_expenses(self, sgna_expenses):
    self.sgna_expenses = sgna_expenses

  def set_operating_expenses(self, operating_expenses):
    self.operating_expenses = operating_expenses
  
  def set_operating_income(self, operating_income):
    self.operating_income = operating_income

  def set_non_operating_income(self, non_operating_income):
    self.non_operating_income = non_operating_income
  
  def set_net_income(self, net_income):
    self.net_income = net_income

  def set_shares_outstanding(self, shares_outstanding):
    self.shares_outstanding = shares_outstanding

  def set_earnings_per_share(self, earnings_per_share):
    self.earnings_per_share = earnings_per_share