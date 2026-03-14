import subprocess
import json
import threading

class MCPClient:
    def __init__(self, name, command, args):
        self.name = name
        self.process = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self.id_counter = 1
        self.responses = {}

        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        for line in self.process.stdout:
            try:
                msg = json.loads(line.strip())
                if "id" in msg:
                    self.responses[msg["id"]] = msg
            except:
                pass

    def request(self, method, params=None):
        request_id = self.id_counter
        self.id_counter += 1

        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }

        if params:
            payload["params"] = params

        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

        while request_id not in self.responses:
            pass

        return self.responses.pop(request_id)

    def initialize(self):
        return self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "python-mcp-client",
                    "version": "1.0"
                }
            }
        )

    def list_tools(self):
        return self.request("tools/list")

    def call_tool(self, name, arguments):
        return self.request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments
            }
        )
