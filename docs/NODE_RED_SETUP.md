# Node-RED HMI Setup

The supplied flow uses **FlowFuse Dashboard 2** and communicates only with the OpenPLC Modbus server at `127.0.0.1:502`.

## 1. Install the required nodes

Open PowerShell in the Node-RED user directory. On Windows this is normally `%USERPROFILE%\.node-red`:

```powershell
cd "$env:USERPROFILE\.node-red"
npm install @flowfuse/node-red-dashboard@1.30.2 @flowfuse/node-red-dashboard-2-ui-led@1.1.0 node-red-contrib-modbus@5.60.1
```

This project uses FlowFuse Dashboard 2, not the older `node-red-dashboard` package. The LED status indicators in the supplied flow additionally require `@flowfuse/node-red-dashboard-2-ui-led`.

The versions above are the versions used to verify `node_red/flows.json`. Keeping them aligned makes the imported HMI reproducible.

## 2. Start Node-RED

```powershell
node-red
```

Open the editor at [http://127.0.0.1:1880](http://127.0.0.1:1880).

## 3. Import the project flow

1. Open the Node-RED menu in the upper-right corner.
2. Select **Import**.
3. Select the repository file `node_red/flows.json` or paste its contents.
4. Choose **Import to new flow**.
5. Select **Deploy**.

The imported Modbus client is already configured for OpenPLC at `127.0.0.1:502`, unit ID `1`.

## 4. Open the dashboard

After deploying, open the Dashboard 2 link shown in Node-RED. The usual local address is:

```text
http://127.0.0.1:1880/dashboard/conveyor-hmi
```

If Node-RED generated a different page path, use the Dashboard link in the editor sidebar.

## 5. Verify the connection

Start the complete system in this order:

1. Python digital twin
2. OpenPLC Runtime and PLC program
3. Node-RED flow

The Modbus nodes should show a connected state. Pressing **Start** should change the system status and begin generating products in the Python terminal.

## Troubleshooting

- **Unknown dashboard or LED nodes:** install `@flowfuse/node-red-dashboard@1.30.2` and `@flowfuse/node-red-dashboard-2-ui-led@1.1.0`, then restart Node-RED.
- **Unknown Modbus nodes:** install `node-red-contrib-modbus@5.60.1` and restart Node-RED.
- **Connection refused on port 502:** start OpenPLC Runtime and confirm its Modbus server is enabled.
- **Dashboard opens but values do not change:** deploy the flow and verify the Modbus nodes connect to `127.0.0.1`, port `502`, unit ID `1`.

Return to the [main project README](../README.md) for the full project overview.
