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
    Then I should see "Promotion REST API Service"
    And  I should not see "404 Not Found"

Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Macbook" in the results
    And I should see "iwatch" in the results
    And I should not see "iphone" in the results