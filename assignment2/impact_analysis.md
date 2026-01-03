# Impact Analysis – Organisation Controller

## 1. Addressed Component / Module

This impact analysis focuses on the **Organisation Registry** module in the
Sahana-Eden legacy system. Specifically, the analysis targets the
`organisation()` RESTful CRUD controller function located in
`controllers/org.py`.

The `organisation()` function serves as the main entry point for organisation
management, handling operations such as creating, editing, and listing
organisations.

---

## 2. Impact Analysis Graph (Call Graph)

**Graph Type:** Call Graph

The Call Graph illustrates the execution flow and dependencies starting from
an incoming HTTP request to the organisation management endpoint. The main
call sequence is as follows:

- User HTTP request to `/org/organisation`
- `organisation()` controller function in `controllers/org.py`
- `s3db.org_organisation_controller()` in the model/controller layer
- CRUD framework (S3CRUD)
- Database tables related to organisations (e.g. `org_organisation`)
- Response returned to the client (HTML or JSON)

This graph highlights how control is passed from the controller layer to the
model and database layers during organisation-related operations.

---

## 3. Impact and Insights

The impact analysis shows that the `organisation()` function is a key
dependency within the organisation management workflow. Any modification to
this controller or the underlying model-layer controller may have ripple
effects on organisation creation, editing, and listing functionalities.

Changes to the organisation data schema or CRUD logic could also affect other
modules that rely on organisation data. Therefore, modifications to this
function should be carefully assessed to avoid unintended side effects across
the system.
