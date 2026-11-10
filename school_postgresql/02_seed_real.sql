-- Reálná DEV/RANDOM data ze zdrojového Git commitu 1dfbaff02eed608b2c95a7c6d96d427b2239d6d0
-- Původ: chráněné soubory zůstávají NEDOTČENÉ; TEST není importován.
-- 3 evidence zdrojových PDF názvů, 2 dataset verze, 45 skutečných otázek,
-- 62 normalizovaných gold evidence řádků (50 zdrojových skupin), 4 historické dokumentované souhrny.
-- PDF ani původní JSONL nejsou ve veřejném repozitáři: neoznačovat za verifikované.
BEGIN;

INSERT INTO school_rag.documents(source_filename) VALUES
    ('Cisco_IP_Addressing_Services_Guide_2026.pdf'),
    ('Cisco_IP_Routing_Configuration_Guide_2026.pdf'),
    ('Cisco_OSPF_Configuration_Guide_2026.pdf')
ON CONFLICT (source_filename) DO NOTHING;

INSERT INTO school_rag.evaluation_datasets
  (dataset_name,source_path,source_git_blob_sha,source_commit_sha)
VALUES
    ('dev', 'rag_api_project/eval/dev_questions.json', '7e38960197dcde252c8aa047ee626c645d8158e2', '1dfbaff02eed608b2c95a7c6d96d427b2239d6d0'),
    ('random', 'rag_api_project/eval/random_questions.json', '8a301867e0218dbfdde8d458b293c0b9863a2758', '1dfbaff02eed608b2c95a7c6d96d427b2239d6d0')
ON CONFLICT (dataset_name,source_git_blob_sha) DO NOTHING;

-- Skutečné otázky, přepis 1:1 bez úprav obsahu.
WITH payload(dataset_name,source_git_blob_sha,external_question_id,topic,question_text) AS (
VALUES
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_001', 'flooding-reduction', 'What happens to LSAs when OSPF flooding reduction is enabled?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 'passive-interface', 'What command is used to configure a passive interface in OSPF?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_003', 'virtual-link', 'What is the purpose of an OSPF virtual link?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_004', 'cost-calculation', 'How does OSPF calculate the cost of an interface?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_005', 'router-id', 'How does OSPF select the router ID?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_006', 'nssa-external-routes', 'How does an OSPF NSSA ABR advertise external routes into the backbone?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_001', 'dhcp-relay', 'What command specifies the DHCP packet forwarding address on a relay agent?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_002', 'dhcp-option-82', 'How can an Option-82-capable DHCP server use the remote ID and circuit ID?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'routing_dev_001', 'administrative-distance', 'What does administrative distance represent in IP routing?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_001', 'slaac', 'What information from a Router Advertisement does a SLAAC client use to form its IPv6 address?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_001', 'nat-inside-source', 'What happens to the inside local source address during NAT inside source translation?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcpv6_dev_001', 'dhcpv6-relay-link-address', 'How does a DHCPv6 server determine which address pool to use for a relayed client request?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_002', 'pat-overload', 'How does PAT distinguish multiple inside hosts that share one global IP address?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_002', 'duplicate-address-detection', 'What is the purpose of IPv6 Duplicate Address Detection?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'routing_dev_002', 'default-route', 'Why are default routes used on routers that do not have routes to all networks?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'rip_dev_001', 'rip-hop-count', 'What does a hop count of 16 mean in RIP?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'eigrp_dev_001', 'eigrp-feasible-successor', 'What is the role of a feasible successor in EIGRP?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'bgp_dev_001', 'bgp-local-preference', 'When comparing BGP local preference values, which value is preferred?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_003', 'neighbor-discovery', 'Which IPv4 mechanisms does IPv6 Neighbor Discovery replace?'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_003', 'dhcp-snooping', 'What two functions does DHCP snooping use to provide network security?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_001', 'bgp-med', 'When BGP compares routes from the same neighboring AS, which MED value is preferred?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'dhcp_random_001', 'dhcp-address-binding', 'What does an address binding represent in the Cisco IOS DHCP server database?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_001', 'ipv6-ra-guard', 'What does IPv6 RA Guard do with unwanted or rogue Router Advertisement packets from clients?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'nat_random_001', 'dynamic-nat', 'How does dynamic NAT obtain global addresses for translating unregistered IP addresses?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'routing_random_001', 'route-redistribution', 'What does route redistribution do between routing protocols?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'rip_random_001', 'rip-split-horizon', 'On which interfaces does RIP split horizon prevent a router from advertising learned route information?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_001', 'eigrp-stub-query-suppression', 'How does an EIGRP neighbor handle route queries to a device after learning that the device is a stub?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_002', 'bgp-dampening-reuse-limit', 'When is a suppressed BGP route that is up advertised again under route dampening?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_002', 'ipv6-link-local-forwarding', 'Do IPv6 routers forward packets with link-local source or destination addresses to other links?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'dhcp_random_002', 'dhcp-snooping-binding-file-checksum', 'What does the switch use to verify entries when it reads the DHCP snooping binding file?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_003', 'ipv6-dns-aaaa', 'Which DNS resource record type supports IPv6 addresses and is equivalent to an IPv4 A record?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'glbp_random_001', 'glbp-md5-hash-mismatch', 'What does GLBP MD5 authentication do with an incoming packet whose hash does not match the locally generated hash?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_003', 'bgp-peer-group-purpose', 'Why group BGP neighbors with the same update policies into a peer group?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_002', 'eigrp-nsf-restart-signaling', 'Which EIGRP packet-header bit does a newly active switch use to signal an NSF restart and prevent neighbors from resetting the adjacency?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ospf_random_001', 'ospf-link-local-signaling-packets', 'Which OSPF packet types carry additional data in a dedicated link-local signaling TLV block?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'routing_random_002', 'ipv4-classless-supernet-forwarding', 'With classless routing enabled, where does a router forward a packet for a subnet of a network with no default route?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'rip_random_002', 'rip-periodic-update-interval', 'How often does the switch send routing information updates when using RIP?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_003', 'eigrp-reliable-transport-delivery', 'What delivery guarantees does the EIGRP reliable transport protocol provide for EIGRP packets sent to neighbors?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'nat_random_002', 'static-nat-fixed-external-reachability', 'When is static inside source NAT useful for making an inside host accessible from outside?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'tunneling_random_001', 'overlay-tunnel-mtu-overhead', 'According to the guide, by how many octets do overlay tunnels reduce an interface MTU when the basic IPv4 header has no optional fields?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bfd_random_001', 'bfd-failure-detection-routing-response', 'After BFD detects a forwarding-path failure, which component must act to bypass the failed peer?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'msdp_random_001', 'msdp-source-active-message-contents', 'What information does an MSDP source-active (SA) message identify?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'hsrp_random_001', 'hsrp-active-router-failover', 'What happens to control of an HSRP group''s MAC and IP addresses when the designated active router fails?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'wccp_random_001', 'wccp-content-engine-cache-miss', 'What does a WCCP content engine do when requested information is absent from its local cache?'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'tracking_random_001', 'object-tracking-interface-ip-routing-state', 'Which three conditions must be met for a tracked interface IP routing state to be up?')
)
INSERT INTO school_rag.evaluation_questions
  (dataset_id,external_question_id,topic,question_text)
SELECT d.dataset_id,p.external_question_id,p.topic,p.question_text
FROM payload AS p
JOIN school_rag.evaluation_datasets AS d
  ON d.dataset_name=p.dataset_name
 AND d.source_git_blob_sha=p.source_git_blob_sha
ON CONFLICT (dataset_id,external_question_id) DO NOTHING;

-- Normalizované gold evidence: zdrojové pole pages × contains_any se rozvine do
-- jedné (page_number, fragment) dvojice na řádek, bez ztráty OR sémantiky.
-- Původ: přesně 50 skupin gold evidence => 62 atomických řádků (1NF).
WITH payload(dataset_name,source_git_blob_sha,external_question_id,evidence_ordinal,source_filename,page_number,fragment) AS (
VALUES
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_001', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 36, 'devices set the DoNotAge (DNA) bit in their LSAs'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_001', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 36, 'LSAs marked with the DNA bit do not age out'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 28, 'passive-interface type number'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 28, 'Device(config)# passive-interface gigabitethernet 1/0/6'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 447, 'passive-interface router configuration command'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 447, 'passive-interface interface-id'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 448, 'passive-interface router configuration command'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_002', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 448, 'passive-interface interface-id'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_003', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 26, 'Maintains backbone continuity in OSPF'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_003', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 26, 'This establishes a logical connection between two ABRs through a non-backbone'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_003', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 149, 'all areas must be connected to a backbone area'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_003', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 149, 'You can establish a virtual link in case of a backbone-continuity break'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_004', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 26, 'OSPF calculates the cost of an interface based on its bandwidth using the formula'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_004', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 26, 'cost = reference_bandwidth / interface_bandwidth'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_005', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 150, 'OSPF uses the highest IP address configured on the interfaces as its router ID'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_005', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 150, 'OSPF automatically prefers a loopback interface over other interfaces, and it chooses the highest IP address among all loopback interfaces'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_006', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 40, 'NSSA areas use Type-7 LSAs to describe external routes'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ospf_dev_006', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 40, 'The NSSA ABR translates these Type-7 LSAs into Type-5 LSAs (Autonomous System External LSAs) before flooding them into the backbone (Area 0)'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 53, 'you must configure the switch with the ip helper-address address interface configuration command'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 47, 'If the server is option-82-capable, it can use the remote ID, the circuit ID, or both to assign IP addresses and implement policies'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'routing_dev_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 450, 'An administrative distance is a rating of the trustworthiness of a routing information source'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 24, 'Hosts take the first 64 bits of the IPv6 prefix from the Router Advertisement message'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 143, 'the packet gets translated to the corresponding inside global address'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 143, 'The device replaces the inside local source address of host 10.1.1.1 with the inside global address of the translation'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcpv6_dev_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 84, 'the relay includes an address from the client-facing interface (Ethernet 1/0) in the link-address field of a relay-forward message. This address is used by the server to select an address pool'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 144, 'The TCP port numbers act as differentiators.'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'nat_dev_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 144, 'many inside hosts can share the inside global IP address by using many port numbers'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 23, 'request to ensure there is no duplicate IP address on the network'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_002', 2, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 24, 'Duplicate Address Detection is performed by IPv6 clients in order to ensure that random addresses that are picked do not collide with other clients'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'routing_dev_002', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 434, 'A router might not be able to learn the routes to all other networks. To provide complete routing capability, you can use some routers as smart routers and give the remaining routers default routes to the smart router.'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'rip_dev_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 135, 'a network with a hop count of 16 is unreachable'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'eigrp_dev_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 247, 'EIGRP uses the successor as the primary path and feasible successors as repair paths or LFAs'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'bgp_dev_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 292, 'The range is 0 to 4294967295 with the higher value preferred'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'bgp_dev_001', 2, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 298, 'The highest local preference value is preferred'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'bgp_dev_001', 3, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 283, 'Prefer the route with the highest local preference'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'ipv6_dev_003', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 26, 'Neighbor Discovery replaces ARP, ICMP Router Discovery, and ICMP Redirect used in IPv4'),
    ('dev', '7e38960197dcde252c8aa047ee626c645d8158e2', 'dhcp_dev_003', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 45, 'DHCP snooping is a DHCP security feature that provides network security by filtering untrusted DHCP messages and by building and maintaining a DHCP snooping binding database'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 283, 'Prefer the route with the lowest multi-exit discriminator (MED) metric attribute if the neighboring AS is the same for all routes considered'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'dhcp_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 49, 'An address binding is a mapping between an IP address and a MAC address of a host in the Cisco IOS DHCP server database'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 27, 'RA guard increases the security of the IPv6 network by dropping the unwanted or rogue RA packets that come from clients'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'nat_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 142, 'Dynamic address translation (dynamic NAT)—Maps unregistered IP addresses to registered IP addresses from a pool of registered IP addresses'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'routing_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 442, 'Redistributes routes from one routing protocol to another routing protocol'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'rip_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 136, 'Split horizon blocks information about
routes from being advertised by a router on any interface from which that information originated.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 234, 'Any neighbor that receives a packet informing it of the stub status will not query the stub device for any routes,
and a device that has a stub peer will not query that peer.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_002', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 286, 'If the penalty is less than the reuse limit, a suppressed route that is up is advertised again.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 20, 'IPv6 routers do not forward packets with link-local source or destination addresses to other links.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'dhcp_random_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 50, 'Each entry in the file is tagged with a checksum value that the switch uses to verify the entries when it reads
the file.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ipv6_random_003', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 20, 'The DNS AAAA resource record types support IPv6 addresses and are equivalent to an A
address record in IPv4.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'glbp_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 95, 'A keyed hash of an incoming packet is generated and, if the hash within the
incoming packet does not match the generated hash, the packet is ignored.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bgp_random_003', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 285, 'Neighbors with the same update policies can be
grouped into peer groups to simplify configuration and to make updating more efficient.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_002', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 233, 'To prevent an adjacency reset by the neighbors, the new active switch uses a new Restart (RS) bit in the
EIGRP packet header to show the restart.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'ospf_random_001', 1, 'Cisco_OSPF_Configuration_Guide_2026.pdf', 74, 'Link-local signaling provides a mechanism to append additional data to OSPF hello and database description
packets by using a dedicated link-local signaling data block (a TLV structure).'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'routing_random_002', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 84, 'With classless
routing, if a router receives packets for a subnet of a network with no default route, the router forwards the
packet to the best supernet route.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'rip_random_002', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 135, 'Using RIP, the switch sends routing information updates (advertisements) every 30 seconds.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'eigrp_random_003', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 232, 'The reliable transport protocol is responsible for guaranteed, ordered delivery of EIGRP packets to all
neighbors.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'nat_random_002', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 142, 'Static translation is useful when a host on the inside must be accessible by a fixed address from
the outside.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'tunneling_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 88, 'Overlay tunnels reduce the maximum transmission unit (MTU) of an interface by 20 octets (assuming that
the basic IPv4 packet header does not contain optional fields).'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'bfd_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 9, 'BFD is a forwarding path failure detection protocol. BFD detects a failure, but the routing protocol must
act to bypass a failed peer.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'msdp_random_001', 1, 'Cisco_IP_Routing_Configuration_Guide_2026.pdf', 58, 'The SA message identifies the source,
the group the source is sending to, and the address of the RP or the originator ID (the IP address of the interface
used as the RP address), if configured.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'hsrp_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 112, 'HSRP detects when the designated active router fails, and a selected standby router assumes control of the
Hot Standby group''s MAC and IP addresses.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'wccp_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 181, 'If the requested information
is not present, the content engine issues its own request to the originally targeted server to get the required
information.'),
    ('random', '8a301867e0218dbfdde8d458b293c0b9863a2758', 'tracking_random_001', 1, 'Cisco_IP_Addressing_Services_Guide_2026.pdf', 202, 'When you track the IP
routing state, these three conditions are required for the object to be up:
• IP routing must be enabled and active on the interface.
• The interface line-protocol state must be up.
• The interface IP address must be known.')
)
INSERT INTO school_rag.gold_evidence
  (question_id,document_id,evidence_ordinal,page_number,fragment)
SELECT q.question_id,doc.document_id,p.evidence_ordinal,p.page_number,p.fragment
FROM payload AS p
JOIN school_rag.evaluation_datasets AS d
  ON d.dataset_name=p.dataset_name AND d.source_git_blob_sha=p.source_git_blob_sha
JOIN school_rag.evaluation_questions AS q
  ON q.dataset_id=d.dataset_id AND q.external_question_id=p.external_question_id
JOIN school_rag.documents AS doc ON doc.source_filename=p.source_filename
ON CONFLICT (question_id,evidence_ordinal,document_id,page_number,fragment) DO NOTHING;

-- Doložené historické MRR (2026-10-20): hodnoty z docs/en/EVALUATION.md §8.
-- Původní dataset SHA-256 z té doby není doložen. Historický běh NESPOJUJEME
-- FK na současnou revizi DEV/RANDOM; dataset_id zůstává NULL, dataset_label zachová typ.
-- Hit@K pochází ze staršího reportu a není bez originálních JSONL reprodukováno.
WITH raw(dataset_label,retriever,question_count,mrr,h1,h3,h5,h8) AS (
VALUES
    ('dev', 'bm25', 20, 0.7171, 0.60, 0.80, 0.85, 0.90),
    ('dev', 'vector', 20, 0.8321, 0.75, 0.90, 0.90, 0.95),
    ('random', 'bm25', 25, 0.8133, 0.72, 0.92, 0.92, 0.92),
    ('random', 'vector', 25, 0.6050, 0.44, 0.72, 0.80, 0.84)
)
INSERT INTO school_rag.evaluation_runs
  (dataset_label,retriever,run_date,question_count,mrr,
   hit_at_1,hit_at_3,hit_at_5,hit_at_8,
   record_kind,source_reference,provenance_note)
SELECT r.dataset_label,r.retriever,DATE '2026-10-20',r.question_count,r.mrr,
       r.h1,r.h3,r.h5,r.h8,'documented_baseline',
       'docs/en/EVALUATION.md#en-8-historical-baseline-2026-10-20',
       'Historical summary only. Dataset revision unknown, dataset_id NULL. Original JSONL, PDF corpus and Chroma index absent; Hit@K not independently reproduced.'
FROM raw AS r
WHERE NOT EXISTS (
  SELECT 1 FROM school_rag.evaluation_runs AS existing
  WHERE existing.dataset_label=r.dataset_label
    AND existing.retriever=r.retriever
    AND existing.run_date=DATE '2026-10-20'
    AND existing.record_kind='documented_baseline'
);
COMMIT;
