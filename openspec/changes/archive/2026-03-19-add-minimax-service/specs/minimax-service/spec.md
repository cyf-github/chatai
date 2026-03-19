## ADDED Requirements

### Requirement: Minimax gRPC service implements Chat RPC
The system SHALL provide a gRPC `MinimaxService` (or `MinMaxService` per proto naming) that implements the shared Chat RPC. The service SHALL forward chat requests to the Minimax API via an OpenAI-compatible client and return a `ChatResponse` with `reply` or error fields.

#### Scenario: Successful chat request
- **WHEN** a client sends a valid `ChatRequest` with non-empty messages to MinimaxService
- **THEN** the service calls Minimax API and returns a `ChatResponse` with `reply` containing the model's text response

#### Scenario: Empty messages rejected
- **WHEN** a client sends a `ChatRequest` with no messages
- **THEN** the service returns a `ChatResponse` with `error_code="INVALID_REQUEST"` and `error_message="messages required"`

#### Scenario: API error propagated
- **WHEN** the Minimax API returns an error or raises an exception
- **THEN** the service returns a `ChatResponse` with `reply=""` and `error_message` set to a descriptive string

### Requirement: Minimax service configuration via environment
The Minimax service SHALL read configuration from environment variables: `MINIMAX_API_KEY` (required for API calls) and `MINIMAX_MODEL` (optional, default `M2-her`).

#### Scenario: Default model used when MINIMAX_MODEL unset
- **WHEN** `MINIMAX_MODEL` is not set
- **THEN** the service uses model `M2-her` for API calls

#### Scenario: Custom model when MINIMAX_MODEL set
- **WHEN** `MINIMAX_MODEL` is set to a valid model name
- **THEN** the service uses that model for API calls
