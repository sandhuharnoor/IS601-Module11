# IS601 Module 11 - Reflection

## What I Learned

This assignment helped me better understand how SQLAlchemy, Pydantic, and PostgreSQL work together in a Python application. I learned how to represent calculations as database models, validate incoming data, and verify that records are stored and retrieved correctly.

I also gained more experience with automated testing and Docker. One important lesson was that passing unit tests does not necessarily mean the entire application is working correctly.

## Challenges and Solutions

One challenge was extending the existing calculation model without breaking its original functionality. The application already supported calculations with multiple operands, while the assignment required individual a and b fields. I updated the model and schemas to support the required fields while preserving the existing calculation behavior.

Another challenge was testing PostgreSQL safely. I used dedicated test databases to avoid interfering with other project data. I then verified that calculation records could be inserted and retrieved with the correct operands, operation type, and result.

I also worked through an end-to-end testing issue involving the Python interpreter used by the FastAPI subprocess. Updating the test fixture to use the active interpreter helped resolve the problem.

## Testing and Verification

I added tests for all four arithmetic operations, invalid calculation types, missing operands, division by zero, and database persistence.

The final local test run completed successfully with 110 passing tests and 100% statement coverage.

I also built and ran the application in Docker and verified that its health endpoint responded successfully.

## CI/CD and Security

I configured a GitHub Actions workflow to run automated tests using PostgreSQL, perform a Trivy vulnerability scan, and publish the Docker image to Docker Hub after successful checks.

This helped me understand how testing, security scanning, and deployment can be connected in an automated development workflow.

## Final Takeaway

My biggest takeaway from this assignment was the importance of verifying software at multiple levels. Unit tests check individual functionality, integration tests verify database interactions, and end-to-end tests help confirm that the application works as expected.

This assignment strengthened my understanding of database persistence, automated testing, Docker, and CI/CD.
