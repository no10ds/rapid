# 0001 - Query endpoint
Date: 2022-03-08

## Status
Accepted

## Context

While brainstorming the support of complex queries, i.e., limit, sort, filter, group by, and aggregate operations, we considered three industry-known solutions:
- Accepting raw SQL
- Using GraphQL for querying several API endpoints
- SQL query as a JSON request body

To decide, we considered rAPId service design and features, the threat of SQL injection, ease of use, and ease of implementation. We discuss each of the solutions below:

#### Accepting raw SQL
This solution allows high flexibility in the contents of the query and is easy to implement. On the flip side, it comes with the threat of SQL injections. Moreover, the client needs to be experienced with writing SQL queries.

<ins>Conclusion</ins>: This solution exposes the API to malicious SQL injection and might be too low level for non-IT users.

#### Using GraphQL for querying several API endpoints

This approach is incompatible with rAPId API since we don't have fixed entities that a GraphQL object could represent.

Consider an example for which GraphQL is a good solution

- `/employee/<employee-id>/first_name`
- `/employee/<employee-id>/last_name`
- `/employee/<employee-id>/email_address`

Here, the `employee` always has `id`, `first_name`, `last_name`, and `email_address`, so we can create separate endpoints to get this information and call them with the GraphQL object.

However, in rAPId API, we have datasets with different column names and values, so each dataset structure might be very different.

<ins>Conclusion</ins>: This solution is not applicable for rAPID API because datasets are not fixed entities.


#### SQL query as a JSON request body

By sending a JSON request, we can support all required SQL queries -  and just them. Thus, we are in control of the contents of the query.

The SQL query is broken into different JSON properties. For example, the following query:

`SELECT destination, time FROM completed_journeys`

is represented as JSON property:

`select_columns: ["destination", "time"]`

through the `/datasets/trains/completed_journeys/query` endpoint.

<ins>Conclusion</ins>: This solution may be too verbose for those who prefer using raw SQL. However, it supports all the required query operations, is safer than raw SQL, and easier to use for clients without experience with SQL. Thus, we chose it as our solution for supporting complex queries.

## Decision
We decided to use JSON request body to query the dataset.

See the Query Dataset section [usage guide](../../guides/usage/usage.md) for the template of the JSON request body and examples.

This solution is complemented by the WAF SQL injection rule, which blocks web requests that contain malicious SQL code in the JSON body.

## Consequences

Clients can query the dataset through JSON request body and only with SQL commands that we support. Those are: select columns from a given dataset, filter by single or multiple conditions, group by columns, order by columns (in ascending or descending order), aggregate, and limit by the number of rows.
Any attempt at injecting a different SQL query operation (for example INSERT or DELETE), will throw an error: either for incorrect values or for being captured by the WAF SQL injection rule.
