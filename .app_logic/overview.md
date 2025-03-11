# Overview
A collection of AI tools and agents for army personnel, packaged as a Docker container. 

## Tech Stack
- Python
- Django
- Docker
- LLM Integration (to be determined)
- RAG (Retrieval Augmented Generation)
- Neon.tech Postgres DB (serverless)

## Application Structure

### Django Apps
1. **core** - Base application with shared components
   - Landing page (no rate limiting)
   - Tool page rate limiting (Cloudflare FORWARD_FROM_IP_HEADER)
   - Common utilities

2. **pacenote_foo** - PaceNoteFoo LLM workflow
   - Chat interface
   - simple A > B chat, no need for conversation history
   - RAG implementation
   - LLM integration

3. **policy_foo** - PolicyFoo LLM workflow
   - Chat interface
   - RAG implementation
   - LLM integration

### Pages
1. Landing Page - Introduction and navigation to tools
2. PaceNoteFoo Tool - Chat interface for the PaceNoteFoo workflow
3. PolicyFoo Tool - Chat interface for the PolicyFoo workflow

## Deployment
- Containerized with Docker
- Environment variables for configuration



