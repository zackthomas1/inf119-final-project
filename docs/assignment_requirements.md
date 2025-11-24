# Instructions on implementation details:

The core functionalities that must be included are:
1. Multi-agent system with MCP integration
a. Design and implement a multi-agent system that uses MCP for communication
between agents.
b. Define the roles of each agent, the tools they have access to, and the
collaboration strategy amongst them.
c. A README.md file on how to run your system.
d. The system should be batteries-included. Please include the necessary tooling,
servers, and clients required to support the MCP framework. We should be able
to run your system using only the instructions you provided.
2. User interface
a. Receive the description and requirements that you signed up for.
b. Return the code for the given application. The code should be runnable, clearly
satisfying each input requirement. We do not look for the correctness of the
generated code, so general bugginess is ok as long as every input requirement is
satisfied.
c. Return the test cases corresponding to the generated code. This should be
runnable, and should pass with at least 80% accuracy, with a minimum of 10 test
cases.
d. Both b) and c) should come with an instruction on how to run them.
3. Model usage tracking
a. Track and report the usage of each model in the system.
i. Number of API calls to each model
ii. Total token used for each model
b. The report should be in a format of JSON, with the following structure:
{“model1”: {“numApiCalls”: number, “totalTokens”: number}, ...}
c. The tracking code should be clearly commented so that we can see how it is
done. Please do not try to fabricate numbers.
