

# **Expert Application Specification: Python MCP Server and Gemini LLM Router**

## **I. System Architecture and Technology Stack (The Blueprint)**

### **1.1 Project Goals and Mandate: LLM Gateway/MCP Server Role**

The objective of this specification is the development of a high-performance, resilient, and secure Python server implementing the Model Context Protocol (MCP). This server will function as an intelligent LLM Gateway for the Windsurf Cascade client. MCP is a protocol that enables Large Language Models (LLMs) to access custom tools and services. By implementing the MCP specification, the Windsurf/Cascade client gains native integration, allowing it to leverage the custom capabilities and context provided by this server.

The core mandate of this service is to act as an LLM orchestrator and router. In this role, the server must simplify the complex process of integrating multiple LLM providers and models, abstracting away the differing Application Programming Interfaces (APIs) and specializing prompt engineering across diverse applications. The primary benefit of this gateway approach is cost optimization and capability matching, ensuring that user queries are dynamically routed to the most appropriate LLM from the defined Gemini model pool based on task complexity, cost, and latency profiles.

Crucially, the server provides a single point of control for managing security, observability, and resource consumption. The architectural decision to implement an MCP Gateway provides robust decoupling: the Windsurf client only needs to interface with the standardized MCP protocol (e.g., via tools/call), while the server manages the internal complexities of vendor-specific API calls, routing algorithms, and error handling. This separation allows future optimizations—such as switching model providers or adjusting routing weights—to be implemented solely by updating the server, without requiring modifications to the client application or its configuration. The required public endpoint for this service, using the standard HTTP transport supported by Windsurf, should be https://\<your-server-url\>/mcp.

### **1.2 Architectural Decision Rationale: FastAPI for ASGI Performance**

The selection of the Python web framework is critical due to the inherent high-latency nature of external LLM API communications. Traditional synchronous frameworks, such as Flask, execute tasks sequentially, leading to performance bottlenecks when waiting for time-consuming network operations to complete. Benchmarks indicate that synchronous frameworks using Gunicorn might handle around 4,000 to 5,000 requests per second (req/sec).

To meet the requirements of modern AI applications, particularly those aiming for high-volume, low-latency tasks—a specific use case targeted by the Gemini 2.5 Flash-Lite model —the application must utilize an asynchronous framework. FastAPI, built upon the ASGI (Asynchronous Server Gateway Interface) standard and typically deployed with Uvicorn, is mandatory for this project. FastAPI’s native support for asynchronous request handling allows the server to initiate multiple non-blocking I/O operations concurrently, achieving significantly higher performance, potentially handling 20,000+ req/sec. This capability is foundational to managing high-throughput traffic and ensuring responsiveness when querying the high-speed Flash-Lite model.

Furthermore, FastAPI's deep integration with the Pydantic library provides several non-negotiable architectural advantages. Pydantic is used for rigorous data validation and schema definition. This is crucial for protocol compliance in two ways:

1. **MCP Tool Definition:** The Model Context Protocol requires tool definitions to be exposed via JSON Schema for client introspection. Pydantic models automatically generate this required JSON Schema.  
2. **LLM Structured Output:** Pydantic models are used to enforce structured output from the Gemini models for critical internal tasks, such as the initial query routing decision (Triage Engine), ensuring machine-readability and data integrity.

The use of Pydantic thus establishes a unified layer for schema definition, validating data across all three components: the external MCP client interface, the internal FastAPI request handling, and the upstream Gemini Function Calling API integration.

### **1.3 System Components and Data Flow Diagram**

The application is logically separated into distinct layers to ensure modularity, maintainability, and clear separation of concerns, supporting a robust LLM application stack.

1. **Transport Layer (FastAPI/Uvicorn):** Handles the physical connection, manages the ASGI event loop, and routes all incoming HTTP requests to the single /mcp path operation.  
2. **Security Layer (FastAPI Dependencies):** Implements mandatory client authentication using FastAPI’s Dependency Injection system. This layer verifies the client's API key before processing the JSON-RPC payload, ensuring that only authenticated users can access the LLM resources.  
3. **MCP Handler Layer:** Parses the incoming JSON-RPC 2.0 requests. It handles two primary methods:  
   * tools/list: Responds with the JSON Schema definitions for all available LLM-invocable tools.  
   * tools/call: This is the entry point for executing LLM actions, which initiates the Orchestration flow described below.  
4. **LLM Orchestration Layer (The Gateway):** This layer embodies the core business logic, executing a systematic workflow:  
   * **Triage Engine:** The system employs a low-cost, high-speed model (Gemini 2.5 Flash-Lite) to rapidly classify the user query's intent (e.g., CODE\_GEN, SIMPLE\_QUERY) by forcing a structured Pydantic response.  
   * **Dynamic Dispatcher:** Based on the Triage Engine’s classification, the dispatcher routes the full query to the optimal target model (gemini-2.5-pro, gemini-2.5-flash, etc.), considering current availability and load.  
   * **Execution/Fallback Manager:** This module executes the chosen model request, manages the two-step Function Calling workflow (if tools are involved), and implements necessary resiliency features like retries, timeouts, and fallbacks to ensure service stability.

### **1.4 Secure Configuration Management (Environment Variables and Secrets)**

Security best practices mandate that all sensitive credentials, particularly API keys, must be strictly managed outside of the application source code. API keys are highly sensitive, and compromising them can lead to unauthorized access, unexpected quota usage, and significant financial charges.

The primary method for configuration loading MUST rely on environment variables. The following procedures are required:

1. **Source Control Exclusion:** The application’s repository MUST contain a .gitignore file that explicitly excludes all environment files (e.g., .env) to prevent accidental key commitment.  
2. **Upstream Authentication Key:** The key used to authenticate the server with Google's Gemini API (GEMINI\_API\_KEY) must be loaded as an environment variable once upon application initialization. This key is kept secure on the backend server, preventing exposure to the client-side environment, which is a critical security vulnerability.  
3. **Client Access Keys:** The keys used by Windsurf/Cascade to authenticate against the MCP server must be managed securely, ideally via a Key Management Service (KMS) or loaded from a secure configuration store.

The server architecture distinguishes between two key types: the internal, upstream Gemini key (authorizing the server's access to the model) and the client key (authorizing the user's access to the server). The application design must ensure the upstream key is static and securely loaded, while the client keys are validated dynamically on a per-request basis using the security layer.

## **II. Security and Client Authentication Implementation**

The stability and financial viability of the LLM Gateway depend fundamentally on strict authentication and access control. Unauthorized usage of the gateway, which uses a shared, secure upstream Gemini API key, could lead to unexpected charges and service interruption.

### **2.1 Client Authentication Service: API Key Validation via FastAPI Dependencies**

Authentication of the Windsurf/Cascade client MUST be enforced at the entry point of the FastAPI application using standard HTTP API Key schemes. The prescribed mechanism utilizes FastAPI’s Dependency Injection system, which ensures security checks are mandatory for all protected endpoints.

The server will require the client to supply an API key within a custom HTTP header. The recommended implementation uses fastapi.security.APIKeyHeader:

Python

\# Conceptual Implementation Detail  
from fastapi.security import APIKeyHeader  
\# Use X-API-Key as the standard header name for client identification  
api\_key\_scheme \= APIKeyHeader(name="X-API-Key", auto\_error=False)

async def verify\_client\_key(client\_key: str \= Depends(api\_key\_scheme)):  
    \# Validation logic here  
    \# Check key against database or configuration list  
    \# If invalid, raise HTTPException(status\_code=401)  
    pass

By defining the authentication logic as a dependency, all path operation functions—specifically the core /mcp endpoint—can be protected by simply including Depends(verify\_client\_key) in their signature. This centralized approach minimizes code repetition and guarantees systematic security enforcement across the entire protocol surface.

### **2.2 Secure Validation Logic and Storage**

The verify\_client\_key function is responsible for determining if the provided key is valid and belongs to an authorized client. If the incoming request lacks the necessary Authorization header or the key is invalid, the dependency injection system will immediately raise an HTTPException returning a 401 Unauthorized status code, halting further processing of the request.

For enterprise deployments, the validation process must involve a secure lookup (e.g., querying a dedicated user database or a secure Key Management System). If the system is deployed behind an API management platform, the key validation may occur upstream, but the application must still be configured to trust and integrate with this external security context.

The implementation of robust client authentication serves a dual purpose beyond mere access control:

1. **Service Protection:** It ensures that the LLM resources, which are accessed using a shared upstream key, are not subject to unauthorized or malicious requests.  
2. **Cost and Resource Management:** The key validation process must tie the request back to a specific client identity. This identity can then be used by the server to enforce strict rate limits, quotas, and potentially different pricing tiers, thereby actively managing the financial risk associated with LLM consumption and preventing a single client from monopolizing quota. The ability to allocate unique API keys per team member, as recommended by security guidelines, further supports granular accountability and auditing.

## **III. Model Context Protocol (MCP) Core Service**

The MCP Server communicates using JSON-RPC 2.0 messages over the prescribed HTTP transport. The server must strictly adhere to this protocol for successful integration with the Windsurf Cascade client.

### **3.1 MCP Transport Layer Specification**

All communication for tool discovery and invocation must occur at the /mcp endpoint using HTTP. While standard HTTP is required, the specification strongly recommends implementing support for **Streamable HTTP** or Server-Sent Events (SSE) to handle the inherently streaming nature of LLM responses efficiently.

All requests and responses must conform to the JSON-RPC 2.0 structure. A distinguishing feature of MCP is that the request ID field (id) MUST be a string or integer and **MUST NOT be null**.

**Table: Standard JSON-RPC 2.0 Message Structure**

| Field | Type | Description | Requirement |
| :---- | :---- | :---- | :---- |
| jsonrpc | String | Protocol version, always "2.0" | Mandatory |
| id | String | Number | Unique request identifier | Mandatory (non-null) |
| method | String | Name of the procedure to invoke (e.g., tools/list, tools/call) | Mandatory |
| params | Object | Array | Parameters passed to the method | Optional |
| result | Any | The return value for successful execution (in Response) | Present on Success |
| error | ErrorObject | Error information if processing failed (in Response) | Present on Failure |

### **3.2 Tool Discovery Implementation (tools/list)**

The server must implement the tools/list method, which is invoked by the MCP client to discover the capabilities available for the LLM to use. The response payload defines each tool available on the server.

A tool definition MUST include a unique name, a description explaining its functionality, and an inputSchema detailing the expected parameters. Importantly, these schemas must be provided in the JSON Schema format.

In this application, Pydantic models serve as the single source of truth for all tool definitions. Defining the tool's input and output structures as Pydantic classes streamlines the process, as Pydantic automatically generates the necessary JSON Schema for the MCP tools/list response. This consistency ensures that the declared tool capabilities are accurately reflected to the Windsurf client.

### **3.3 Tool Invocation Endpoint Specification (tools/call)**

The tools/call method is the MCP mechanism for invoking a specific tool discovered during the tools/list phase. When a client receives a tool call request from the LLM agent (e.g., Cascade), it forwards the invocation request to the server via this method.

The server's response to a tools/call request must return the tool's output wrapped in the JSON-RPC result object. This result structure includes:

1. **content:** A human-readable text summary of the tool's execution (e.g., "Current weather is 72°F").  
2. **structuredContent:** An optional, but highly recommended, JSON Schema object defining the structured data output.

The inclusion of structuredContent is crucial for performance and reliability. When the tool execution result is passed back to the LLM for synthesis (as detailed in Section V), providing reliable, structured JSON data allows the model to process the information contextually and accurately, reducing the potential for misinterpretation or hallucination compared to relying solely on a text summary. The entire function execution and result wrapping process must be designed to run asynchronously, minimizing execution latency within the high-performance ASGI framework.

## **IV. Advanced LLM Gateway and Model Routing Engine**

The core value proposition of this application is its ability to intelligently route incoming requests across the heterogeneous Gemini model pool, balancing cost efficiency, performance, and analytical capability.

### **4.1 Defined Model Pool and Performance Benchmarks**

The Gemini 2.5 model family offers a tiered structure of capability and cost, which is ideally suited for model routing. The gateway must support the integration of four distinct models, each assigned specific roles within the routing architecture.

LLM Gateway Model Pool Specification

| Model ID | Primary Capability | Ideal Use Case (Routing) | Cost/Latency Profile |
| :---- | :---- | :---- | :---- |
| gemini-2.5-pro | Complex Reasoning, Code/STEM, Long Context | Code analysis, complex tool orchestration, large dataset summarization | Highest Cost, Highest Latency |
| gemini-2.5-flash | Balanced performance, thinking, function calling | General coding, high-quality content generation, complex data tasks | Medium Cost, Low Latency |
| gemini-2.5-flash-lite | Fastest, most cost-efficient multimodal | High-throughput classification, translation, *Query Triage* | Lowest Cost, Lowest Latency |
| gemini-2.0-flash | Legacy performance, reliable general use | Fallback/Deprecation layer, simpler I/O tasks | Low Cost, Low Latency |

The requirement to support Gemini 2.5 Pro for tasks like analyzing large codebases or complex reasoning, contrasted with the high-volume, low-latency requirements of Gemini 2.5 Flash-Lite, mandates a dynamic routing engine that can distinguish between these use cases.

### **4.2 Routing Logic: Intent Classification and Task-Based Delegation**

The routing mechanism is implemented via a Triage Engine, which minimizes overall latency and cost by directing the user's query to the optimal model quickly.

#### **4.2.1 Triage Model Selection and Rationale**

The Triage Engine MUST use **Gemini 2.5 Flash-Lite**. This model is selected specifically because it is the fastest and most cost-efficient option available. Routing decisions must be near-instantaneous, and using a higher-cost model (like Pro) just to determine the route would introduce unnecessary cost and latency to every request, negating the purpose of the optimization.

#### **4.2.2 Structured Triage Output using Pydantic Schema**

The efficiency of the Triage Engine relies on enforcing structured output. The incoming user prompt is first sent to Gemini 2.5 Flash-Lite with a system prompt instructing it to classify the intent and fill a predefined Pydantic schema: RouteDecision.

Python

\# Pydantic Schema for Triage Decision  
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):  
    """Schema defining the LLM router's output decision for dispatch."""  
    task\_type: str \= Field(description="Classification of the user's intent: CODE\_GEN, COMPLEX\_ANALYSIS, SIMPLE\_QUERY, etc.")  
    model\_preference: str \= Field(description="Suggested Gemini model ID (e.g., 'gemini-2.5-pro').")  
    confidence\_score: float \= Field(description="Model's confidence (0.0 to 1.0) in its classification.")

The server passes the user query to Flash-Lite, forcing the response into this JSON structure. The parser then ingests the result, which allows for robust, non-ambiguous determination of the optimal downstream model without relying on complex string parsing or slow LLM reasoning chains.

Based on the parsed task\_type and model\_preference, the Dynamic Dispatcher routes the original request to the targeted model, adhering to a policy such as: CODE\_GENERATION tasks, which require powerful reasoning, are explicitly dispatched to gemini-2.5-pro. Conversely, requests classified as SIMPLE\_QUERY are handled by the low-cost gemini-2.5-flash-lite. The architecture must be modular, allowing for future expansion to dynamic routing, where the dispatcher might also consider real-time metrics like current model load or observed latency before making the final choice.

### **4.3 Resiliency and Fallback Mechanisms**

A resilient gateway must manage inevitable service fluctuations, outages, and internal failures. The following measures are mandatory:

1. **Request Timeouts:** Clear timeout thresholds MUST be established for each model. For instance, the high-latency gemini-2.5-pro might be allocated 60 seconds, while the lower-latency Flash models are allocated 10-20 seconds. If a model fails to respond within this window, the request must be terminated to prevent application hang.  
2. **Fallback Chains:** If the targeted model (e.g., Pro) returns an error or times out, the Dispatcher MUST implement a structured fallback strategy. The request is automatically rerouted to the next most capable model in the hierarchy (e.g., Pro → Flash → Flash-Lite). This ensures service continuity even if the primary premium model is temporarily unavailable.  
3. **Circuit Breaker Pattern:** To prevent continuous attempts against an unhealthy model that is experiencing an extended outage or high failure rate, a circuit breaker must be implemented. This component monitors error thresholds and temporarily removes the failing model from the available routing pool. This avoids unnecessary retries and ensures that traffic is rerouted preemptively until the unhealthy model recovers.

## **V. Tool Execution Layer and Function Calling Workflow**

The integration of the MCP tool definition with the underlying Gemini Function Calling API is crucial. The server must effectively translate the generic protocol request (tools/call) into the vendor-specific, multi-turn LLM interaction required for execution.

### **5.1 Integrating Gemini Function Calling with MCP Tooling**

Gemini models utilize function calling to determine when to invoke external functions based on the user's natural language request, effectively serving as an RPC (Remote Procedure Call) mechanism to external systems. The model requires the tools (functions) to be described using JSON Schema declarations.

The MCP server acts as the runtime environment for these function calls. The server must unify the tool definition such that a single Pydantic definition generates the schema necessary for both the client (MCP tools/list) and the model (Gemini Function Declaration). This single source of truth ensures consistency and simplifies maintenance.

### **5.2 The Asynchronous Two-Step LLM Interaction Process for Tool Use**

To successfully execute an LLM tool call initiated by the Windsurf client, the server must internally orchestrate a multi-turn conversation with the chosen Gemini model. The client sees this as a single tool/call request, but the server handles the underlying complexity.

The standard Function Calling workflow requires two distinct calls to the Gemini API, performed asynchronously within the FastAPI environment:

#### **Step 1: Model Decision (Intent to Call)**

1. The server transmits the user's prompt, along with the complete list of available Function Declarations (Pydantic-generated JSON Schemas), to the selected Gemini model (e.g., Pro or Flash).  
2. The model analyzes the prompt and determines if a function call is necessary.  
3. If a function is deemed necessary, the model returns a response containing a structured JSON object that details the function name and the recommended arguments (parameters) to use.

#### **Step 2: Server Execution and Result Injection (Final Synthesis)**

1. The server intercepts the model’s function call request from Step 1\.  
2. The server executes the actual, corresponding Python function locally (this function performs the external action defined by the MCP tool). This is a high-performance, asynchronous execution designed to minimize the time the server spends waiting.  
3. The result of this execution is captured, preferably as a structured Pydantic object to ensure reliability.  
4. The server then sends a **second** request to the Gemini model. This request includes the original prompt and conversation history, the initial tool call request from the model, and the actual tool execution result from step 3\.  
5. The model uses the injected tool result as a new context to synthesize the final, human-readable text response. This final text, along with the optional structured content, is then wrapped in the JSON-RPC tools/call result and returned to the Windsurf client.

This two-step process demonstrates how the LLM Gateway functions as a sophisticated agent orchestrator, managing the conversation state and external tool interactions that occur transparently to the client application.

### **5.3 Deployment Considerations**

To maintain the high-performance and availability mandates of the specification, the application MUST be prepared for a scalable production environment:

1. **Containerization:** The entire Python application, including all dependencies (FastAPI, Pydantic, Gemini SDK), MUST be packaged within a standard container (Docker) to guarantee environmental consistency across development, staging, and production environments.  
2. **ASGI Server:** The application MUST be deployed using a robust ASGI server like Uvicorn.

## **Conclusions and Recommendations**

This Application Specification details a robust, expert-level Python MCP server designed to serve as an intelligent LLM Gateway for Windsurf/Cascade. The design prioritizes performance, cost efficiency, and security through carefully selected architectural components.

**Key Prescriptive Requirements:**

1. **Mandatory Framework Selection:** The use of **FastAPI** over synchronous frameworks is mandated to ensure asynchronous I/O handling, which is non-negotiable for meeting the high-volume, low-latency requirements associated with the Gemini 2.5 Flash-Lite model.  
2. **Schema-Driven Development:** **Pydantic** must be employed universally—for client authentication, internal data integrity, MCP tool definition, and, most critically, enforcing structured outputs for the Triage Engine and tool result injection. This maximizes the reliability of machine-to-machine communication, enhancing both routing accuracy and final response quality.  
3. **Flexible Model Usage:** The architecture must default to the Flash-Lite-based Triage Engine model. This methodology ensures that the decision layer (routing) is the least costly operation, preventing the deployment from incurring unnecessary expense by routing simple queries to premium models. Other tools expose access to other models.  
4. **Security Implementation:** Client API key validation using FastAPI Dependencies (APIKeyHeader) must be implemented across all protected endpoints to enforce access control and facilitate future rate limiting and quota management, thereby protecting the shared upstream Gemini credentials.  
5. **Resilience Protocol:** The LLM Orchestration layer must include robust error handling against upstream service interruptions and maintain service availability.