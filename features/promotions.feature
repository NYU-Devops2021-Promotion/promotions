Feature: The promotions service back-end
          As a e-commercial web
          I need a RESTful catalog service
          So that I can keep track of all my promotions

Background:
    Given the following promotions
        | product_name       | category | product_id | amount | from_date  | to_date    |
        | Macbook            | Discount | 11111      | 10     | 2021-10-07 | 2022-10-07 |
        | iwatch             | BOGOF    | 11112      | 20     | 2021-10-07 | 2022-10-07 |
        | iphone             | BOGOF    | 11112      | 30     | 2021-10-07 | 2022-10-07 |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Promotion REST API Service" in the title
    And  I should not see "404 Not Found"

Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Macbook" in the results
    And I should see "Discount" in the results
    And I should see "11111" in the results
    And I should see "10" in the results
    And I should see "2021-10-07" in the results
    And I should see "2022-10-07" in the results
    And I should see "iwatch" in the results
    And I should see "iphone" in the results
    And I should see "BOGOF" in the results

Scenario: Create all promotions
    When I visit the "Home Page"
    And I set the "product_id" to "11114"
    And I set the "product_name" to "iPad"
    And I select "Discount" in the "category" dropdown
    And I set the "amount" to "15"
    And I set the "description" to "Great Deal"
    And I set the "from_date" to "10-07-2021"
    And I set the "to_date" to "10-07-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "product_id" field should be empty
    And the "product_name" field should be empty
    And the "category" field should be empty
    And the "amount" field should be empty 
    And the "from_date" field should be empty
    And the "to_date" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "11114" in the "product_id" field
    And I should see "iPad" in the "product_name" field
    And I should see "Discount" in the "category" dropdown
    And I should see "15" in the "amount" field
    And I should see "Great Deal" in the "description" field
    And I should see "2021-10-07" in the "from_date" field
    And I should see "2022-10-07" in the "to_date" field

Scenario: Read all promotions
    When I visit the "Home Page"
    And I set the "product_id" to "11113"
    And I set the "product_name" to "iPod"
    And I select "Discount" in the "category" dropdown
    And I set the "amount" to "15"
    And I set the "description" to "Great Deal"
    And I set the "from_date" to "10-07-2021"
    And I set the "to_date" to "10-07-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "product_id" field should be empty
    And the "product_name" field should be empty
    And the "category" field should be empty
    And the "amount" field should be empty 
    And the "from_date" field should be empty
    And the "to_date" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "11113" in the "product_id" field
    And I should see "iPod" in the "product_name" field
    And I should see "Discount" in the "category" dropdown
    And I should see "15" in the "amount" field
    And I should see "Great Deal" in the "description" field
    And I should see "2021-10-07" in the "from_date" field
    And I should see "2022-10-07" in the "to_date" field

Scenario: Update a promotion
    When I visit the "Home Page"
    And I select "Discount" in the "category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Discount" in the "category" dropdown
    When I select "BOGOF" in the "category" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "BOGOF" in the "category" dropdown

Scenario: Query a promotion
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I press the "Best" button
    Then I should see the message "Success"
    And I should see "11111" in the "product_id" field
    And I should see "Macbook" in the "product_name" field
    And I should see "Discount" in the "category" dropdown
    And I should see "10" in the "amount" field
    And I should see "Great Deal" in the "description" field
    And I should see "2021-10-07" in the "from_date" field
    And I should see "2022-10-07" in the "to_date" field