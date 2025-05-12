-- Written by: Christoph Hänisch (with the help of ChatGPT)
-- Last Change: 2025-05-12
-- License: LGPL v3.0 or later (see LICENSE file)

-- Define the MIDI over LAN protocol
midi_lan_proto = Proto("MIDI_over_LAN", "MIDI over LAN Protocol")

-- Define the protocol fields
local f_header_mark = ProtoField.string("midilan.header_mark", "Header Mark")
local f_version = ProtoField.uint8("midilan.version", "Version", base.DEC)
local f_packet_type = ProtoField.uint8("midilan.packet_type", "Packet Type", base.DEC, {
    [0] = "MIDI Message",
    [1] = "Hello",
    [2] = "Hello Reply"
})
local f_device_name_length = ProtoField.uint8("midilan.device_name_length", "Device Name Length", base.DEC)
local f_device_name = ProtoField.string("midilan.device_name", "Device Name")
local f_midi_data = ProtoField.bytes("midilan.midi_data", "MIDI Data")
local f_num_device_names = ProtoField.uint8("midilan.num_device_names", "Number of Device Names", base.DEC)
local f_id = ProtoField.uint32("midilan.id", "ID", base.DEC)
local f_hostname_length = ProtoField.uint8("midilan.hostname_length", "Hostname Length", base.DEC)
local f_hostname = ProtoField.string("midilan.hostname", "Hostname")
local f_ip_address = ProtoField.ipv4("midilan.ip_address", "IP Address")

midi_lan_proto.fields = {
    f_header_mark, f_version, f_packet_type, f_device_name_length, f_device_name,
    f_midi_data, f_num_device_names, f_id, f_hostname_length, f_hostname, f_ip_address
}

-- Create the dissector function
function midi_lan_proto.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = midi_lan_proto.name

    local subtree = tree:add(midi_lan_proto, buffer(), "MIDI over LAN Protocol Data")

    -- Parse the header
    subtree:add(f_header_mark, buffer(0,4))
    subtree:add(f_version, buffer(4,1))
    local packet_type = buffer(5,1):uint()
    subtree:add(f_packet_type, buffer(5,1))

    -- Parse the payload based on packet type
    if packet_type == 0 then
        -- MIDI Message Packet
        local device_name_length = buffer(6,1):uint()
        subtree:add(f_device_name_length, buffer(6,1))
        subtree:add(f_device_name, buffer(7, device_name_length))
        subtree:add(f_midi_data, buffer(7 + device_name_length))
    elseif packet_type == 1 then
        -- Hello Packet
        subtree:add(f_id, buffer(6,4))
        local hostname_length = buffer(10,1):uint()
        subtree:add(f_hostname_length, buffer(10,1))
        subtree:add(f_hostname, buffer(11, hostname_length))
        local num_device_names = buffer(11 + hostname_length,1):uint()
        subtree:add(f_num_device_names, buffer(11 + hostname_length,1))
        
        local offset = 12 + hostname_length
        for i = 1, num_device_names do
            local device_name_length = buffer(offset,1):uint()
            subtree:add(f_device_name_length, buffer(offset,1))
            subtree:add(f_device_name, buffer(offset + 1, device_name_length))
            offset = offset + 1 + device_name_length
        end
    elseif packet_type == 2 then
        -- Hello Reply Packet
        subtree:add(f_id, buffer(6,4))
        subtree:add(f_ip_address, buffer(10,4))
        local hostname_length = buffer(14,1):uint()
        subtree:add(f_hostname_length, buffer(14,1))
        subtree:add(f_hostname, buffer(15, hostname_length))
        local num_device_names = buffer(15 + hostname_length,1):uint()
        subtree:add(f_num_device_names, buffer(15 + hostname_length,1))
        
        local offset = 16 + hostname_length
        for i = 1, num_device_names do
            local device_name_length = buffer(offset,1):uint()
            subtree:add(f_device_name_length, buffer(offset,1))
            subtree:add(f_device_name, buffer(offset + 1, device_name_length))
            offset = offset + 1 + device_name_length
        end
    end
end

-- Register your protocol on the specified UDP port
local udp_port = DissectorTable.get("udp.port")
udp_port:add(56129, midi_lan_proto)
