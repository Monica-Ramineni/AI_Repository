## Session 15 – Assignment: Questions & Answers

### ❓ Question #1:
What are the core components of an `AgentCard`?

#### ✅Answer :

An **AgentCard** is a standardized metadata structure that describes an AI agent's capabilities, contact information, and communication preferences. It's essentially a "digital business card" that enables agents to discover and communicate with each other through the A2A protocol.

The core components of an AgentCard include:

🔹 **name**: The display name that identifies the agent (e.g., "General Purpose Agent")

🔹 **description**: A clear explanation of what the agent does and its capabilities

🔹 **url**: The endpoint where other agents can reach this agent

🔹 **version**: The current version number for compatibility tracking

🔹 **default_input_modes**: What types of input the agent accepts (text, images, etc.)

🔹 **default_output_modes**: What types of output the agent can provide

🔹 **capabilities**: Special features like streaming responses or push notifications

🔹 **skills**: Specific abilities the agent has, each with examples and descriptions

🔹 **preferred_transport**: The communication protocol and transport method the agent prefers (e.g., HTTP, WebSocket, gRPC)

🔹 **contact_information**: How to reach the agent's maintainers or support team

🔹 **authentication_requirements**: What authentication methods the agent supports

🔹 **rate_limits**: Any usage restrictions or rate limiting policies

Think of it as a comprehensive "business card" that tells other agents exactly what this agent can do, how to reach it, and how to work with it effectively.

### ❓ Question #2:
Why is A2A (and other such protocols) important in your own words?

#### ✅Answer :

A2A protocols are crucial because they:

🔹 Create a Common Language: Just like humans need a shared language to communicate, AI agents need a standardized way to talk to each other

🔹 Enable Teamwork: Different agents can work together on complex tasks, each doing what they're best at

🔹 Prevent Duplication: Instead of every agent rebuilding the same tools, they can share capabilities through the network

🔹 Improve Reliability: Standardized communication means fewer errors and better error handling when things go wrong

🔹 Speed Up Development: Developers can focus on building specialized agents rather than reinventing basic communication

🔹 Enable Composability: Lets you chain specialized agents (search, RAG, analysis) into end-to-end workflows

🔹 Scale Services: One well-implemented agent can serve many clients/agents, creating reusable services

🔹 Reduce Integration Friction: Teams can evolve agents independently behind a stable protocol

It's like creating an "AI internet" where agents can discover each other's services and collaborate seamlessly, making the whole system more powerful than any single agent could be alone.


