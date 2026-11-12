# Local AI Agent & Customer Support Automation

A self-hosted AI environment for experimenting with local language models, connecting external AI APIs, and developing AI-powered customer-support workflows.

> **Project status:** This repository combines a Python/FastAPI customer-agent prototype with a local AI environment based on Ollama and Open WebUI. Open WebUI is the chat interface; it is not the FastAPI agent itself. Platform-specific customer-chat automation (for example, automatically reading or replying to messages on marketplaces) requires a separate integration and is **not implied to be available out of the box**.

## Table of Contents

- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
  - [Quick Start: Open WebUI + Local Ollama](#quick-start-open-webui--local-ollama)
  - [Quick Start: Customer Agent API](#quick-start-customer-agent-api)
  - [Quick Test](#quick-test)
- [Installation Guide](#installation-guide)
  - [Requirements](#requirements)
  - [Windows with WSL 2](#windows-with-wsl-2)
  - [Docker and Open WebUI](#docker-and-open-webui)
  - [Ollama and Local Models](#ollama-and-local-models)
  - [Customer Agent Setup](#customer-agent-setup)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Integrations and Extensions](#integrations-and-extensions)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Roadmap](#roadmap)
- [License](#license)

---

## Introduction

This project explores how to build and operate an AI environment on personal hardware or a dedicated server. It brings together a model runtime, a browser-based interface, and a Python API application to provide a practical starting point for AI experimentation and automation.

The long-term direction is customer-support assistance: receiving a customer message, passing it to an AI model, and returning a useful response. The initial environment can be used independently for chatting with models, testing prompts, and evaluating responses before more advanced integrations are added.

## Project Overview

The environment has three distinct parts:

1. **Ollama — model runtime:** downloads and runs supported language models on the machine. When a model runs locally, inference does not require a per-request provider API charge; hardware, electricity, and storage still have costs.
2. **Open WebUI — web interface:** provides a browser-based chat experience for selecting available models, starting conversations, and reviewing chat history.
3. **Customer Agent — application/API layer:** a Python application built with FastAPI. Its `/message` endpoint accepts a customer identifier and message, sends the message to the configured AI provider, and returns the generated response.

These components are related but separate. Open WebUI is for interactive use; the Customer Agent endpoint is intended to be called by another application or integration.

## Features

### Available in the current setup

- Self-hosted Open WebUI in Docker.
- Persistent Open WebUI data through a named Docker volume.
- Local model execution through Ollama (when Ollama and a compatible model are installed).
- Browser-based model selection and chat.
- Conversation history and chat management in Open WebUI.
- FastAPI application with a health endpoint and a message endpoint.
- Provider-based response generation through an API configuration.

### Intended / requires additional work

- Connecting marketplace or store inboxes (such as Divar or Torob).
- Automatically detecting unanswered customer messages.
- Sending generated replies back to a platform.
- Multi-account management, scheduling, approval queues, and production monitoring.

These capabilities need platform-specific API access, webhooks, permissions, and integration code. They should not be considered enabled merely by installing Open WebUI or running the current FastAPI application.

## Screenshots

The screenshots below illustrate the Open WebUI interface.

### Chat Interface

The main screen is the entry point for interacting with a selected model. Write a prompt in the message composer, send it, and review the generated response in the conversation.

![Open WebUI chat interface](https://github.com/user-attachments/assets/86743f04-fc09-48ad-a3ad-cc3c70b8da41)

### Choosing a Model

Use the model selector to switch between models available to Open WebUI. Different models may vary in response quality, latency, memory requirements, and suitability for a task. The models shown in this screenshot are examples of models available in that environment—not a guarantee that every installation has the same list.

![Selecting a model in Open WebUI](https://github.com/user-attachments/assets/1b64c0cb-841f-439a-a30f-4bdd8b5d45bd)

### Conversation View

A conversation displays user prompts and model responses in sequence. It is useful for testing instructions, comparing outputs, and iterating on a prompt before using it in an application.

![Example AI conversation](https://github.com/user-attachments/assets/1b64c0cb-841f-439a-a30f-4bdd8b5d45bd)

### Managing Chats

The chat sidebar provides access to previous conversations. Use it to return to an earlier discussion or keep separate chats for different experiments and tasks.

![Open WebUI chat management](https://github.com/user-attachments/assets/c56e96f3-00d5-4f95-bde1-dea17f23d491)

## Architecture

```text
                       Browser / User
                            |
                +-----------+-----------+
                |                       |
                v                       v
         Open WebUI                 Client App
         (port 3000)                    |
                |                        v
                |                 Customer Agent
                |                  (FastAPI)
                |                        |
                +----------+-------------+
                           |
                           v
                    Model Provider
                    /            \
                   v              v
              Ollama          External API
           (local model)   (e.g. OpenRouter)
```

**Important:** Open WebUI and FastAPI are separate entry points. Open WebUI connects to a model provider for interactive chats. The Customer Agent calls its configured provider from application code. They can use the same provider, but one does not automatically route messages through the other.

## Technology Stack

| Technology | Role |
|---|---|
| Ubuntu / WSL 2 | Linux development and server environment |
| Docker | Runs Open WebUI in an isolated container |
| Docker volumes | Persist Open WebUI data across container recreation |
| Ollama | Runs supported language models locally |
| Open WebUI | Browser-based interface for model conversations |
| Python | Customer Agent implementation |
| FastAPI | HTTP API framework for the agent |
| Uvicorn | ASGI server used to run FastAPI |
| HTTPX | HTTP client for provider requests |
| Pydantic | Request data validation |
| python-dotenv | Loads environment variables from `.env` |

## Quick Start

This section is the shortest route to a working environment. For detailed explanations, see [Installation Guide](#installation-guide).

### Quick Start: Open WebUI + Local Ollama

**1. Start Open WebUI**

Run this in a terminal with Docker access:

```bash
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

**2. Run Ollama and download a model**

Install Ollama first (see [Ollama and Local Models](#ollama-and-local-models)), then:

```bash
ollama pull qwen3:0.6b
```

Make sure Ollama is running. On systems where it is not managed as a service, run:

```bash
ollama serve
```

**3. Open the interface**

Visit **http://localhost:3000**, sign in/create the initial account, and select the model from the model selector.

> If Open WebUI is running in Docker while Ollama runs on the host, configure the Ollama connection using an address reachable from the container. `localhost` inside a container refers to that container, not automatically to the host machine.

### Quick Start: Customer Agent API

The following commands assume the project source contains `main.py` and the dependencies described below.

**1. Enter the project and activate its virtual environment**

```bash
cd ~/projects/customer-agent
source .venv/bin/activate
```

**2. Configure the provider key**

Create `.env` in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Do not commit this file or share the key.

**3. Run the API**

```bash
uvicorn main:app --reload
```

**4. Open the interactive API docs**

Visit **http://127.0.0.1:8000/docs** and try `POST /message`.

### Quick Test

Send a test message from another terminal:

```bash
curl -X POST http://127.0.0.1:8000/message \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"test-001","message":"سلام، محصول موجوده؟"}'
```

A successful response contains the submitted `customer_id`, the received message, and an `ai_response` generated by the configured provider. Exact response content depends on the selected model and provider availability.

## Installation Guide

### Requirements

- Windows 10/11 with WSL 2, or a Linux distribution such as Ubuntu.
- Docker Desktop (Windows) with WSL integration, or Docker Engine on Linux.
- Python 3.10+ recommended for the FastAPI application (use the version supported by the project's dependencies).
- Ollama only if you want local inference.
- Enough RAM, disk space, and compatible hardware for the model you choose. Model requirements vary considerably; a small model is a practical starting point.
- Internet access to download container images, Python packages, and model files, and to reach external APIs if used.

### Windows with WSL 2

1. Install/enable WSL 2 and an Ubuntu distribution.
2. Open Ubuntu and create/use your Linux user.
3. Install Docker Desktop on Windows.
4. In Docker Desktop, enable WSL integration for the Ubuntu distribution.
5. Verify Docker access from the environment where you intend to run commands:

```bash
docker --version
docker ps
```

If Docker commands work in Windows PowerShell but not in Ubuntu, check Docker Desktop's WSL integration. Avoid changing permissions on Docker Desktop's internal sockets as a workaround.

### Docker and Open WebUI

Start Open WebUI:

```bash
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

Open **http://localhost:3000**.

Useful lifecycle commands:

```bash
docker ps                         # list running containers
docker logs -f open-webui         # follow Open WebUI logs
docker stop open-webui            # stop
docker start open-webui           # start existing container
docker restart open-webui          # restart
```

The `open-webui` volume stores persistent application data. Removing a container does not remove this named volume. **Do not run `docker volume rm open-webui` unless you intentionally want to delete its stored data.**

### Ollama and Local Models

1. Install Ollama using its official installation instructions for your operating system.
2. Confirm it is available:

```bash
ollama --version
```

3. Download a model (example):

```bash
ollama pull qwen3:0.6b
```

4. Test it directly:

```bash
ollama run qwen3:0.6b
```

5. If Ollama is not running as a service, start it in a terminal:

```bash
ollama serve
```

6. Connect Open WebUI to Ollama. The connection URL must be reachable from the Open WebUI container. In Docker Desktop environments, the host may be reachable through `host.docker.internal`; confirm this in your own setup and configure the Ollama connection accordingly.

Local inference avoids provider API usage for generation, but model downloads consume disk space and inference uses local CPU/GPU/RAM.

### Customer Agent Setup

**1. Get the source code**

Clone the repository (replace the placeholder with the actual repository URL):

```bash
git clone <REPOSITORY_URL>
cd customer-agent
```

If the project is already on your machine, enter its directory instead.

**2. Create a Python virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

Install the packages used by the application:

```bash
pip install fastapi uvicorn httpx python-dotenv pydantic
```

If the repository has a `requirements.txt`, prefer:

```bash
pip install -r requirements.txt
```

**4. Create environment configuration**

```bash
touch .env
```

Add the provider key:

```env
OPENROUTER_API_KEY=your_api_key_here
```

**5. Run FastAPI**

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive documentation is at `http://127.0.0.1:8000/docs`.

## Configuration

### Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `OPENROUTER_API_KEY` | Authentication for OpenRouter requests made by the current agent implementation | Yes, when using OpenRouter |

Create `.env` in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Ensure `.env` is listed in `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
```

Never place API keys in source code, screenshots, public issues, or committed files.

### Model Selection

- **Local model:** downloaded and served by Ollama; choose a model based on your hardware and task.
- **API model:** configured through a provider and its credentials; availability, pricing, and rate limits depend on that provider.
- OpenWebUI's selected model and the Customer Agent's provider/model configuration are separate settings unless explicitly connected in code/configuration.

## Usage Guide

### Using Open WebUI

1. Open `http://localhost:3000`.
2. Select a model from the model selector.
3. Start a new chat and enter a prompt.
4. Review the response and continue the conversation.
5. Use the chat sidebar to return to previous conversations or keep topics separate.

### Using the Customer Agent

The current API accepts a customer identifier and a message:

```json
{
  "customer_id": "customer-001",
  "message": "Hello, is this item available?"
}
```

The agent sends the message to the configured AI provider and returns the generated text in its API response. At this stage, this is an API-based message processing flow; it does not automatically read or send messages to a marketplace inbox.

## API Documentation

### `GET /`

Health/status endpoint.

Example:

```bash
curl http://127.0.0.1:8000/
```

Expected shape:

```json
{
  "status": "running",
  "agent": "customer-agent"
}
```

### `POST /message`

Accepts a customer message and returns an AI-generated response.

**Request body:**

| Field | Type | Description |
|---|---|---|
| `customer_id` | string | Identifier for the customer/conversation |
| `message` | string | Incoming customer message |

Example:

```bash
curl -X POST http://127.0.0.1:8000/message \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"customer-001","message":"سلام، چطور سفارش بدم؟"}'
```

Example response shape:

```json
{
  "customer_id": "customer-001",
  "received_message": "سلام، چطور سفارش بدم؟",
  "ai_response": "..."
}
```

The `ai_response` value is generated dynamically; it is not a fixed response.

### Interactive API Docs

FastAPI automatically provides Swagger UI:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI schema:** http://127.0.0.1:8000/openapi.json

Use `/docs` to inspect request schemas and execute API calls interactively.

## Integrations and Extensions

The agent can serve as an API layer for other software. A typical integration would:

1. Receive a message from an external system (webhook, API polling, or another supported mechanism).
2. Normalize the message into the agent's request format.
3. Call `POST /message`.
4. Review, approve, or process the generated response.
5. Send the response back through the external platform's API.

### Messaging and Marketplace Platforms

Connecting platforms such as Telegram, Divar, Torob, or an online store requires platform-specific support. Before implementing an integration, verify:

- Whether the platform exposes an official messaging API or webhook.
- Authentication and account permissions.
- Whether reading messages and sending replies are both permitted.
- Rate limits, security requirements, and platform terms.
- Whether human approval is required before sending an AI-generated response.

**An API key for an AI provider is not an API key for a marketplace or messaging platform.** Provider connectivity generates text; platform integration is responsible for retrieving and delivering messages.

## Troubleshooting

### Open WebUI does not open

Check whether the container is running and whether port `3000` is published:

```bash
docker ps --filter name=open-webui
docker logs --tail 100 open-webui
```

Open `http://localhost:3000`. If the container is unhealthy or the application is not responding, inspect its logs and health status before deleting or recreating it. Preserve the `open-webui` volume.

### Docker command is unavailable in Ubuntu/WSL

- Confirm Docker Desktop is running.
- Enable WSL integration for the correct Ubuntu distribution.
- Run `docker ps` from that distribution.
- Do not change permissions on Docker Desktop internal sockets as a routine fix.

### Open WebUI cannot connect to Ollama

- Confirm Ollama is running (`ollama list` / `ollama serve`).
- Confirm the model has been downloaded.
- Use an address reachable from inside the Open WebUI container; container `localhost` is not the host.
- Check provider/connection settings in Open WebUI.

### FastAPI returns an API-key error

- Confirm `.env` is in the same project directory from which the app is launched.
- Confirm the variable name is exactly `OPENROUTER_API_KEY`.
- Restart Uvicorn after changing environment configuration.
- Never paste the secret key into logs, chat, or public issue reports.

### Provider request fails

Check network access, provider account status, API key validity, model availability, and provider rate limits. The agent cannot generate a provider response if the upstream service is unreachable or rejects the request.

## Security Notes

- Keep API keys in environment variables or a secret manager.
- Do not commit `.env`.
- Do not expose FastAPI or Open WebUI publicly without authentication, TLS, firewall rules, and an appropriate deployment configuration.
- Treat customer messages and AI-generated responses as potentially sensitive data.
- Review AI responses before automatically sending them to customers, especially for pricing, availability, refunds, or other business commitments.
- Follow each connected platform's policies and access requirements.

## Roadmap

Potential next steps:

- [ ] Improve agent configuration and provider/model selection.
- [ ] Add conversation context and persistent customer sessions.
- [ ] Add structured logging and error handling.
- [ ] Implement a Telegram integration.
- [ ] Investigate supported marketplace/store messaging integrations.
- [ ] Add human approval before sending replies.
- [ ] Add a dashboard for message status and response review.
- [ ] Prepare a production deployment with authentication and monitoring.

## License

No license has been specified yet. Add a license before distributing or accepting contributions; until then, reuse and redistribution permissions are not explicitly granted.
