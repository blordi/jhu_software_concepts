# Graduate Admissions Analytics Dashboard

Created by Benjamin Lordi: F83F95 for JHU Modern Software Concepts in Python on 9.19.25

## About
This project was created for Module 4, assignment 4 Pytest and Sphinx, due on 9.22.25

Link to documentation: https://jhu-sphinx-rtd.readthedocs.io/en/latest/

This project builds upon the Module 3 analytics dashboard by adding comprehensive test coverage and professional documentation. The system provides a complete testing framework with 100% code coverage using pytest, including unit tests, integration tests, and parametrized testing scenarios. Professional documentation is generated using Sphinx with the Read the Docs theme, covering setup instructions, architecture overview, API reference, testing guide, and operational notes. The application maintains all previous functionality - web scraping from The GradCafe, data cleaning with LLM enhancement, PostgreSQL database operations, and a Flask dashboard - while adding robust testing infrastructure and comprehensive documentation for production deployment.

## Approach

This project extends the Module 3 codebase with a comprehensive testing and documentation. The testing suite uses pytest with custom markers (web, buttons, analysis, db, integration) to categorize tests by functionality. Mock objects and fixtures ensure tests are independent and fast, while parametrized tests cover multiple data scenarios efficiently. The test suite includes Flask route testing, database operation verification, data formatting validation, and end-to-end workflow testing with busy-state management.

The documentation system uses Sphinx format to generate professional HTML documentation. The docs include detailed API references with comprehensive docstrings, setup and deployment guides, architecture explanations, testing instructions, and operational troubleshooting guides. All Python modules feature extensive Sphinx-style docstrings with parameter documentation, return types, exception handling, and usage examples. https://jhu-sphinx-rtd.readthedocs.io/en/latest/

## Acknowledgements

The original llm_hosting file came directly from Liv d'Aliberti and was not modified. Some of the regex patterns and SQL queries were assisted by Claude AI. Claude AI also provided guidance on pytest best practices, Sphinx documentation structure, and debugging test failures. The comprehensive docstring format and testing patterns were developed with AI assistance to ensure documentation and test coverage.

## Known Bugs

There are no known bugs at this time. 