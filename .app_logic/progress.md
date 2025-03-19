# Project Progress and Next Steps

## Completed Tasks
- [x] Set up Django project structure with three apps (Core, PaceNoteFoo, PolicyFoo)
- [x] Configure settings with modular structure (base.py and environment-specific settings)
- [x] Clean up redundant settings files
- [x] Configure security headers middleware
- [x] Set up logging configuration
- [x] Configure database connection to Neon DB PostgreSQL
- [x] Create base templates and styling with Bootstrap
- [x] Implement landing page view and template
- [x] Create health check endpoint
- [x] Implement Pace Notes UI with HTML, CSS, and JavaScript
- [x] Set up environment variable configuration with python-dotenv
- [x] Consolidate duplicate base templates
- [x] Integrate Bootstrap styling for consistent UI
- [x] Update project documentation
- [x] Set up NixOS development environment for local development
- [x] Create Dockerfile for production deployment
- [x] Set up Docker Compose for local testing
- [x] Implement Open Router service in Core app
- [x] Implement PaceNote generator API endpoint
- [x] Connect PaceNote UI to backend API
- [x] Implement prompt template handling for PaceNote generation
- [x] Integrate with S3 for competency lists and examples
- [x] Implement PolicyFoo app models structure (skeleton)

## Current Sprint

### Core App
- [x] Create API client base class (S3Service and OpenRouterService)
- [x] Implement Open Router service for LLM integration

### PaceNoteFoo App
- [x] Implement backend API for Pace Notes generation
- [x] Connect to an LLM provider (Open Router with Claude 3.5 Haiku)
- [ ] Implement server-side rate limiting
- [x] Add data validation for user input
- [x] Create response formatting for pace notes

### PolicyFoo App
- [x] Create basic data models for policy documents, queries and responses (skeleton)
- [ ] Implement ChatInterfaceView
- [ ] Create DocumentSearchView
- [ ] Set up PolicyRetriever service

### Infrastructure
- [ ] Implement basic CI/CD pipeline
    - Docker build and push to Docker Hub
    - Github actions

## Backlog

### Core App
- [ ] Add IP-based rate limiting
- [ ] Implement rate limit helper functions
- [ ] Add basic security tests
- [ ] Add caching for S3 resources

### PaceNoteFoo App
- [x] Integrate LLM client
- [x] Implement data validation/sanitization
- [ ] Add more rank options with corresponding competency lists
- [ ] Implement the PaceNote model to store generated notes
- [ ] Add analytics for tracking usage patterns

### PolicyFoo App
- [ ] Implement ChatInterfaceView
- [ ] Create DocumentSearchView
- [ ] Set up PolicyRetriever service
- [ ] Add basic chat template
- [ ] Implement CitationGenerator
- [ ] Add export capability
- [ ] Set up response validation
- [ ] Configure policy document sources

### Infrastructure
- [ ] Configure deployment settings
- [ ] Set up monitoring
- [ ] Implement backup strategy
- [ ] Define resource requirements for containers

### Documentation
- [x] Update PaceNote app documentation
- [ ] Create API documentation
- [ ] Write security guidelines

## Technical Debt
- [ ] Add comprehensive test coverage
- [ ] Improve error handling
- [ ] Add API documentation
- [ ] Write security guidelines
- [ ] Optimize database queries

## Decision Log
- Use NixOS for local development: Better development experience with declarative configuration
- Use Docker for production deployment: Consistent deployment environment across different servers
- Use Bootstrap for UI: Faster development and consistent styling
- Use modular settings structure: Better organization and environment-specific configuration
- Use Neon DB for PostgreSQL: Serverless database with easy connection
- Use Python slim Docker image: Good balance between size and functionality
- Use Open Router with Claude 3.5 Haiku: Good balance of quality, cost, and speed
- Use existing S3 client from Core app: Avoid duplication and leverage existing functionality
- Use existing templates and static files: Maintain consistency across the application

## Open Questions

### Core
- [ ] Decide on analytics tracking for landing page
- [x] Determine rate limit configuration approach (simplified for now)

### PaceNoteFoo
- [x] Identify specific RAG data sources (S3 bucket with competency lists and examples)
- [x] Determine response formatting needs (Two-paragraph structure with titles)
- [x] Define safety controls for generated content (Basic input validation)

### PolicyFoo
- [ ] Identify required policy documents
- [ ] Determine response format requirements
- [ ] Define audit requirements

### Infrastructure
- [x] Which LLM provider should we use? 
    User Response: 
        - decide on a case by case basis
        - Claude 3.5 Haiku for now PaceNoteFoo
- [ ] Do we need user authentication?
- [ ] What are the rate limiting requirements?
- [ ] What are the security requirements?
