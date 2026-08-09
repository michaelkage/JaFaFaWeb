<?php
// ============================================================================
// 1. CORS & PREFLIGHT HEADERS
// ============================================================================
// Allow requests from any origin (e.g., local web front-ends like 127.0.0.1)
header("Access-Control-Allow-Origin: *");
// Specify allowed HTTP methods for browser requests
header("Access-Control-Allow-Methods: GET, OPTIONS");
// Allow custom authorization and payload headers
header("Access-Control-Allow-Headers: Content-Type, X-API-KEY");
// Set response content type to JSON with UTF-8 encoding
header("Content-Type: application/json; charset=UTF-8");

// Handle browser CORS preflight check (OPTIONS request) immediately
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// ============================================================================
// 2. SECURITY & AUTHORIZATION CHECK
// ============================================================================
// Define the expected secret API key for gateway authentication
define('API_KEY', 'AIzaSyDnP5gQ-CWLj1J4xEd0T6xvkboRZI_zoAM');

// Extract API key from either the HTTP request header (X-API-KEY) or the URL query parameter (?api_key=)
$providedKey = $_SERVER['HTTP_X_API_KEY'] ?? $_GET['api_key'] ?? '';

// Terminate execution with 401 Unauthorized if the key is missing or invalid
if ($providedKey !== API_KEY) {
    http_response_code(401);
    die(json_encode(["error" => "Unauthorized gateway access."]));
}

// ============================================================================
// 3. DATABASE CONNECTION CONFIGURATION
// ============================================================================
$host     = "localhost";               // MySQL server hostname
$db_name  = "u819153934_SensorTracking"; // Database name
$username = "u819153934_jafafafqadmin"; // Database username
$password = "1nf0rm@t1c52OOO!!!";       // Database password

try {
    // Initialize PDO instance with exception mode enabled and associative array fetching
    $pdo = new PDO("mysql:host=$host;dbname=$db_name;charset=utf8", $username, $password, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);

    // Check if a specific VehicleId filter parameter was provided in the URL query string
    $vehicleId = $_GET['VehicleId'] ?? $_GET['vehicle_id'] ?? null;

    if ($vehicleId) {
        // Query sensor logs filtered by a specific VehicleId (latest 500 records)
        $stmt = $pdo->prepare("SELECT * FROM VehicleSensors WHERE VehicleId = :vId ORDER BY id DESC LIMIT 500");
        $stmt->execute([':vId' => $vehicleId]);
    } else {
        // Query overall recent sensor logs across all vehicles (latest 500 records)
        $stmt = $pdo->query("SELECT * FROM VehicleSensors ORDER BY id DESC LIMIT 500");
    }

    // Fetch all matching database records into an array
    $rows = $stmt->fetchAll();

    // ============================================================================
    // 4. INLINE RPM DATA DIAGNOSTICS & VARIANCE CHECK
    // ============================================================================
    // Collect all Revolutions_Per_Minute values into a flat list to test data integrity
    $rpmValues = [];
    foreach ($rows as $row) {
        if (array_key_exists('Revolutions_Per_Minute', $row)) {
            $rpmValues[] = (float)$row['Revolutions_Per_Minute'];
        }
    }

    // Default diagnostic output if column is missing from results
    $rpmDiagnostics = ["message" => "Target column 'Revolutions_Per_Minute' was not present in table rows."];

    // Compute metrics if RPM values were found in the database records
    if (count($rpmValues) > 0) {
        $uniqueCount = count(array_unique($rpmValues));
        $minValue    = min($rpmValues);
        $maxValue    = max($rpmValues);
        $variance    = $maxValue - $minValue;

        // Build diagnostic summary report
        $rpmDiagnostics = [
            "total_records_checked" => count($rpmValues),
            "unique_value_count"    => $uniqueCount,
            "min_detected_value"    => $minValue,
            "max_detected_value"    => $maxValue,
            "data_variance"         => $variance,
            "verdict"               => ($variance === 0.0) 
                ? "HARDCODED: The server's database contains identical numbers across all rows. Check your upstream insert pipeline." 
                : "DYNAMIC: The data varies over time on the server."
        ];
    }

    // ============================================================================
    // 5. SUCCESS RESPONSE GENERATION
    // ============================================================================
    // Output standard JSON envelope with result count, diagnostic metrics, and payload
    echo json_encode([
        "status"      => "success",
        "count"       => count($rows),
        "diagnostics" => $rpmDiagnostics,
        "data"        => $rows
    ]);

} catch (Exception $e) {
    // Catch database exceptions and return a formatted 500 Internal Server Error
    http_response_code(500);
    echo json_encode(["error" => "Database read failed", "details" => $e->getMessage()]);
}