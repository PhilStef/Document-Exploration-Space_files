<?php
// save_interactions.php - Endpoint for saving study interaction data
define('DEBUG_FLAG', false); // Set false in production!
function json_response($data, $statusCode = null)
{
    header('Content-Type: application/json');

    // Determine the status code if not explicitly provided
    if ($statusCode === null) {
        $statusCode = isset($data['success']) && $data['success'] ? 200 : 400;
    }

    http_response_code($statusCode);
    echo json_encode($data);
    exit;
}

// CORS setup with specific allowed origins
function setupCORS()
{
    // Define allowed origins
    $allowedOrigins = [
        'https://jeremy-block.github.io/retro-relevance-study/',
        'https://indie.cise.ufl.edu',
        'http://localhost:3576',
        'http://localhost:3000',  // Development environment
        'http://127.0.0.1:3000',  // Alternative development
        'http://localhost:8080',  // testing the Doc Explorer locally.
        'http://127.0.0.1:8080',  // testing the Doc Explorer locally.
        // '',                       // Empty origin for testing locally with postman and no cors
    ];

    // Get the origin header
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';

    // Check if the origin is allowed
    if (DEBUG_FLAG) {
        error_log("Provided origin: " . $origin);
        error_log("allowed origins: " . implode(', ', $allowedOrigins));
    }
    if (in_array($origin, $allowedOrigins)) {
        header("Access-Control-Allow-Origin: $origin");
        header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
        header(header: "Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
        header("Access-Control-Max-Age: 86400"); // Cache preflight for 24 hours

        // Handle preflight OPTIONS request immediately and exit
    } else {
        if (DEBUG_FLAG) {
            json_response(['error' => 'Unauthorized domain', 'origin' => $origin, 'allowed_origins' => $allowedOrigins], 403);
        } else {
            json_response(['error' => 'Unauthorized domain'], 403);
        }
        exit;
    }
}

// Setup CORS before any other output
setupCORS();


if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204); // No Content
    exit;
}

// Accept GET for debugging
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'success', 'message' => 'GET request received, CORS headers set']);
    exit;
}



// Only allow POST method for actual processing
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// Set content type to JSON
header('Content-Type: application/json');
// Configure storage directory
$storageDir = './user_data/';
$requestLog = $storageDir . 'requests.txt';

try {
    $dt = new DateTime('now', new DateTimeZone('America/New_York'));
    file_put_contents($requestLog, "Received request at " . $dt->format('Y-m-d H:i:s') . "\n", FILE_APPEND);

    // Set content size limit (10MB)
    if ($_SERVER['CONTENT_LENGTH'] > 10000000) {
        $error_message = "Payload too large (max 10MB)";
        throw new Exception($error_message);
    }

    // Get the raw POST data
    $jsonData = file_get_contents('php://input');

    // Decode JSON
    $data = json_decode($jsonData, true);

    if (!$data) {
        $error_message = "Invalid JSON data received: " . json_last_error_msg();
        throw new Exception($error_message);
    }

    // Validate required JSON structure
    if (!isset($data['userID']) || !isset($data['filename']) || !isset($data['interactions'])) {
        $error_message = "Missing required fields: userID, filename, and interactions are required.";
        throw new Exception($error_message);
    }

    // Extract data
    $userID = preg_replace('/[^a-zA-Z0-9_-]/', '', $data['userID']);
    $filename = preg_replace('/[^a-zA-Z0-9_.-]/', '', $data['filename']);
    $interactions = $data['interactions'];

    // Add additional security: only allow certain filename patterns
    if (!preg_match('/^interactions_user_[a-zA-Z0-9_-]+\d{1,2}_\d{1,2}_\d{4}__\d{2}_\d{2}_\d{2}_(AM|PM)\.json$/', $filename)) {
        $error_message = "Invalid filename format";
        throw new Exception($error_message);
    }

    // Create directory if it doesn't exist
    if (!is_dir($storageDir)) {
        if (!mkdir($storageDir, 0755, true)) {
            $error_message = "Failed to create storage directory";
            throw new Exception($error_message);
        }
    }

    // Define the full file path
    $filepath = $storageDir . $filename;

    // Save the data
    $result = file_put_contents($filepath, json_encode($interactions, JSON_PRETTY_PRINT));
    // And at successful save
    file_put_contents($requestLog, "Successfully saved file: $filepath\n\n", FILE_APPEND);

    if ($result !== false) {
        // Return success response
        echo json_encode([
            'status' => 'success',
            'message' => 'Interaction data saved successfully',
            'userID' => $userID,
            'filename' => $filename
        ]);

        // Log success
        error_log("Successfully saved interaction data for user $userID to $filepath");
    } else {
        $error_message = "Failed to write data to file";
        throw new Exception($error_message);
    }
} catch (Exception $e) {
    // Log the error
    error_log("Error saving interaction data: " . $e->getMessage());

    file_put_contents($requestLog, ">Error>>>" . $e->getMessage() . "\n\nRaw data >>>\n\n" . $jsonData . "\n\n>>>\n\n", FILE_APPEND);

    // Return error response
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Failed to save interaction data',
        'detail' => $e->getMessage()
    ]);
}
?>