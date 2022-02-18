import copy

class LiquidityPool():

    def __init__(self, year_interest_rate = 36.5):
        """ Creates liquidity pool """

        self.year_interest_rate = year_interest_rate

        # 3x variables to keep track of
        self.lenders = {}
        self.borrowers = {}
        self.liquidity_pool_lenders = 0
        self.liquidity_pool_borrows = 0
        self.interest_rate_factor = 1

        self.time_stamp = 0

        # 3x variable purely for debugging purposes
        self.interest_checker = 0
        self.USDC_add_checker = 0
        self.USDC_remove_checker = 0


    def deposit(self, user_name, USDC_amount, time_gap):
        """ User deposits USDC amount into liquidity pool with time_gap since last transaction """
        # Update time stamp, interest_rate factor, and liquidity pool
        self.time_stamp += time_gap
        self.interest_rate_factor_update(time_gap)
        self.liquidity_pool_update(time_gap, USDC_amount, 0)

        # Create new user if one does not exist
        if user_name not in self.lenders:
            self.lenders[user_name] = {"LP_tokens":0, "LP_factor":0}
        
        # Update a users token, and their LP_factor
        temp_start_balance = copy.deepcopy(self.lenders[user_name]) # ONLY FOR DEBUGGING
        self.lenders[user_name]["LP_factor"] = ((USDC_amount / self.interest_rate_factor) +
                                            self.lenders[user_name]["LP_factor"] * self.lenders[user_name]["LP_tokens"]) / (USDC_amount + self.lenders[user_name]["LP_tokens"]) 
        self.lenders[user_name]["LP_tokens"] += USDC_amount

        # ONLY FOR DEBUGGING
        print(f'{user_name}, Deposit (USDC): {USDC_amount}, (Prior: {temp_start_balance}, Now: {self.lenders[user_name]})') 
        self.USDC_add_checker += USDC_amount


    def withdraw(self, user_name, token_amount, time_gap):
        """ User withdraws a certain amount of LP tokens with time_gap since last transaction"""
        # Update time stamp, interest_rate factor
        self.time_stamp += time_gap
        self.interest_rate_factor_update(time_gap)

        # Calculate how much USDC to return and update lenders
        temp_start_balance = self.lenders[user_name] # ONLY FOR DEBUGGING
        USDC_amount = token_amount * self.lenders[user_name]["LP_factor"] * self.interest_rate_factor
        self.lenders[user_name]["LP_tokens"] -= token_amount

        # Update liquidity pool for amount taken out (principal + interest)
        self.liquidity_pool_update(time_gap, 0, USDC_amount)

        # Remove user if now empty
        if self.lenders[user_name]["LP_tokens"] == 0:
            self.lenders.pop(user_name)

        # ONLY FOR DEMBUGGING
        print(f'Withdraw (USDC): {USDC_amount}, (Prior: {temp_start_balance}, Now: {self.lenders.get(user_name,0)})')
        self.USDC_remove_checker += USDC_amount

    def borrow(self, user_name, USDC_amount, time_gap):
        """ User borrowers a certain amount of USDC at a specific time_gap since last transaction """
        # Update time stamp, interest rate factor, and liquidity pool (we only update for inflows / outflows from lenders)
        self.time_stamp += time_gap
        self.interest_rate_factor_update(time_gap)
        self.liquidity_pool_update(time_gap, 0, 0)

        # Create borrower loan in ledger, and update borrow amount for that specific borrower
        if user_name not in self.borrowers:
            self.borrowers[user_name] = {"borrow_amount":0, "loans":[]}
        self.borrowers[user_name]["loans"].append([USDC_amount, self.time_stamp])
        self.borrowers[user_name]["borrow_amount"] += USDC_amount
        self.liquidity_pool_borrows += USDC_amount

        # ONLY FOR DEBUGGING
        print(f'Borrow (USDC): {USDC_amount}, {user_name} Loans: {self.borrowers[user_name]})') 

    def repay(self, user_name, USDC_amount, loan_number, time_gap):
        """ User repays a certain amount of USDC at a specific time_gap since last transaction """
        # Update time stamp, interest rate factor, and liquidity pool (we only update for inflows / outflows from lenders)
        self.time_stamp += time_gap
        self.interest_rate_factor_update(time_gap)
        self.liquidity_pool_update(time_gap, 0, 0)

        # Calculate the interest earnt so far on that specific loan
        interest = self.interest_income_calculator(self.time_stamp - self.borrowers[user_name]["loans"][loan_number][1], self.borrowers[user_name]["loans"][loan_number][0])
        temp_loan_balance = copy.deepcopy(self.borrowers[user_name]["loans"]) # Only for debugging

        if USDC_amount == "all":
            # Reduce borrowing amount and borrower ledger by principal, calculate how much USDC they have to pay. Remove that loan.
            self.liquidity_pool_borrows -= self.borrowers[user_name]["loans"][loan_number][0]
            self.borrowers[user_name]["borrow_amount"] -= self.borrowers[user_name]["loans"][loan_number][0]
            print(f'{user_name} needs to pay {self.borrowers[user_name]["loans"][loan_number][0]} principal + interest {interest} to cancel loan {loan_number}')
            self.borrowers[user_name]["loans"].pop(loan_number)
        else:
            # Reduce liquidity pool by USDC amount. Update the amount outstanding on the loan.
            self.liquidity_pool_borrows -= USDC_amount
            self.borrowers[user_name]["borrow_amount"] -= USDC_amount
            self.borrowers[user_name]["loans"][loan_number][0] *= (1-(USDC_amount/(self.borrowers[user_name]["loans"][loan_number] + interest)))

        # ONLY FOR DEBUGGING
        print(f'{user_name}, Loans Before: {temp_loan_balance}, Loans After: {self.borrowers[user_name]})') 


    def interest_income_calculator(self, time_gap, amount):
        """ Calculate interest earn't on specific amount in a given time gap """
        return amount * (time_gap / 31536000) * (self.year_interest_rate / 100)


    def liquidity_pool_update(self, time_gap, inflow, outflow):
        """ Update the liquidity pool for interest, outflows and inflows """
        interest = self.interest_income_calculator(time_gap, self.liquidity_pool_borrows)
        self.interest_checker += interest
        self.liquidity_pool_lenders = self.liquidity_pool_lenders + inflow - outflow + interest


    def interest_rate_factor_update(self, time_gap):
        """ Update the interest rate factor since the last transaction """
        if self.liquidity_pool_borrows != 0:
            self.interest_rate_factor = self.interest_rate_factor * (1+ (time_gap / 31536000) * (self.year_interest_rate / 100) * (self.liquidity_pool_borrows / self.liquidity_pool_lenders))

# Only thing to work out is how to apportion the interest on borrowers side. Should we update all of them every time a transaction is made? makes the most sense?
