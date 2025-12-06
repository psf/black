# flags: --preview --line-length=120

matching_routes = [route for route in network_routes if route.destination and router_ip in route.destination_network] + [route for route in network_routes if route.destination is None and route.family == requested_family]

already_wrapped = (
    [route for route in network_routes if route.load_balanced] +
    [route for route in network_routes if route.fallback_route]
)

triple = [route for route in network_routes if route.has_primary and route.supports_failover] + [route for route in network_routes if route.has_secondary and route.supports_failover] + [route for route in network_routes if route.is_backup and route.supports_failover]

# output
matching_routes = (
    [route for route in network_routes if route.destination and router_ip in route.destination_network]
    + [route for route in network_routes if route.destination is None and route.family == requested_family]
)

already_wrapped = (
    [route for route in network_routes if route.load_balanced]
    + [route for route in network_routes if route.fallback_route]
)

triple = (
    [route for route in network_routes if route.has_primary and route.supports_failover]
    + [route for route in network_routes if route.has_secondary and route.supports_failover]
    + [route for route in network_routes if route.is_backup and route.supports_failover]
)
