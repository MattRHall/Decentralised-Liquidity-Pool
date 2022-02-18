# Summary
Decentralized liquidity pools are used in many decentralized finance applications (DeFi). They match up suppliers of assets (which earn interest) with borrowers of assets (which pay interest). This project creates a liquidity pool using Python, which operates on a transactional / ledger basis (suitable for Ethereum based protocols). LP Tokens are used to represent a lenders stake in the liquidity pool.

# Purpose
The purpose of this project was to design a liquidity pool in Python so it could be tested ahead of development. The principle of a liquidity pool itself is simple but there are aspects that make this a challenge.

Firstly, a lender is free to add / withdraw assets to the liquidity pool, and only earns interest when their assets are in the pool. Interest if only paid when assets are withdrawn from the liquidity pool. A mechanism is needed to account for interest accumulated, but without costly unnecessary periodic updates for all users.

Secondly, a lender receives a fixed amount of LP tokens in a 1-1 ratio relative to the amount of USDC stable coins deposited. A mechanism is needed to account for the fact that an LP tokens are not entitled to accumulated interest earnt by LP tokens issued earlier.

# Main Features
- Transactional Based: A transaction is defined as someone depositing, withdrawing, borrowing, or repaying assets / loans. Updates are made every time a transaction is made. This includes calculation of interest since the last transaction, and updating central variables about the liquidity pool.
- Interest Rate Accumulator: Interest is calculated every transaction. The accumulated interest earned by the liquidity pool overtime is monitored. This is used to adjust for LP tokens that deposited later than earlier LP tokens (as so have no accumulated interest attached to them).
- Flexible Repayments: Loans can be repaid early. They must be fully repaid within a certain window. The protocol must be able to handle these situations.
- Timegap: This is the time since the last transaction. The first transaction will have a time gap of 0. 

# Rules / Assertions
- The purpose of this project is to demonstrate functionality. Rules don't exist to control behaviour, e.g. borrowers can't also be lenders, or borrowers can't borrow more than their maximum amount. These can be added when developing.

# Example - 2 borrowers / 2 lenders
```
lp = LiquidityPool()
lp.deposit("Matthew", 500, 0) # Matthew deposits 500 USDC to start.
lp.borrow("Ben", 500, 86400) # Ben borrows 500 USDC 1 day later (86400 seconds)
lp.deposit("James", 500, 86400) # James deposits 500 1 day layer (86400 seconds)
lp.repay("Ben", "all", 0, 86400) # Ben repays all of its loan (principal + interest) 1 day later (86400 seconds)
lp.withdraw("Matthew", 500, 86400*10) # Matthew withdraws all of his tokens 10 days later (86400*10 seconds)
lp.withdraw("James", 500, 86400*5) # James withdraws all of his tokens 5 days later (86400 * 5 seconds)
```
In the scenario above, daily interest is 0.1%. Matthew earns 0.75 interest, as he earns the full interest for 1 day, and then half the interest on the second day. James earns half the interest on the second day (as both Matthew and James have equal amounts in the pool), equal to 0.25. Ben pays 1.0 in interest. 






















