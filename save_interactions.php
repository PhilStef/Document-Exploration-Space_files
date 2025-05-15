<?php
// save_interactions.php - Endpoint for saving study interaction data with improved security

header('Content-Type: application/json');

try {
    // Set content size limit (2MB)
    if ($_SERVER['CONTENT_LENGTH'] > 2000000) {
        throw new Exception("Payload too large (max 2MB)");
    }
    
    // Get the raw POST data
    $jsonData = file_get_contents('php://input');
    
    // Decode JSON
    $data = json_decode($jsonData, true);
    
    if (!$data) {
        throw new Exception("Invalid JSON data received: " . json_last_error_msg());
    }
    
    // Validate required JSON structure
    if (!isset($data['userID']) || !isset($data['interactions']) || !is_array($data['interactions'])) {
        throw new Exception("Required data missing or invalid format");
    }
    
    // Extract userID and interactions
    $userID = $data['userID'] ?? 'unknown';
    $providedFilename = $data['filename'] ?? '';
    $interactions = $data['interactions'] ?? [];
    
    // Sanitize userID (for use in filename)
    $userID = preg_replace('/[^a-zA-Z0-9_\-]/', '', $userID);

    // RATE LIMITING CODE STARTS HERE
    // Check if user has submitted too many requests
    if (!applyRateLimit($userID, 10, 60)) { // 10 requests per 60 seconds
        http_response_code(429);
        echo json_encode([
            'status' => 'error',
            'message' => 'Rate limit exceeded. Please try again later.'
        ]);
        exit;
    }
    
    // Sanitize filename to prevent path traversal
    if (!empty($providedFilename)) {
        $filename = basename($providedFilename); // Strip directory path
        $filename = preg_replace('/[^a-zA-Z0-9_\-\.]/', '', $filename);
    } else {
        $filename = 'interactions_' . $userID . '_' . date('Ymd_His') . '.json';
    }
    
    // Find the end-study event to double-check userID
    $endStudyUserID = null;
    foreach ($interactions as $interaction) {
        if (isset($interaction['event']) && $interaction['event'] === 'end-study' && isset($interaction['userID'])) {
            $endStudyUserID = $interaction['userID'];
            break;
        }
    }
    
    if ($endStudyUserID && $endStudyUserID !== $userID) {
        throw new Exception("User ID mismatch between request and end-study event");
    }
    
    // Use environment variable for data path (fallback to default if not set)
    $basePath = getenv('DATA_STORAGE_PATH') ?: './data/interactions/';
    
    // Ensure the directory exists and is writable
    if (!is_dir($basePath)) {
        if (!mkdir($basePath, 0755, true)) {
            throw new Exception("Failed to create storage directory");
        }
    }
    
    if (!is_writable($basePath)) {
        throw new Exception("Storage directory is not writable");
    }
    
    $filepath = $basePath . $filename;
    
    // Save the data
    $result = file_put_contents($filepath, json_encode($interactions, JSON_PRETTY_PRINT));
    
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
        throw new Exception("Failed to write data to file");
    }
} catch (Exception $e) {
    // During debugging, return verbose error messages
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage(),
        'debug' => [
            'error' => $e->getMessage(),
            'file' => $e->getFile(),
            'line' => $e->getLine()
        ]
    ]);
    error_log("Error saving interaction data: " . $e->getMessage());
}
// Rate limiting function
function applyRateLimit($identifier, $maxRequests, $period)
{
    $rateLimitDir = './rate_limits/';
    if (!is_dir($rateLimitDir)) {
        mkdir($rateLimitDir, 0755, true);
    }

    $rateFile = $rateLimitDir . md5($identifier) . '.json';

    // Get current time
    $now = time();

    // Initialize or load existing rate data
    if (file_exists($rateFile)) {
        $rateData = json_decode(file_get_contents($rateFile), true);
        // Clean up old requests
        foreach ($rateData['requests'] as $key => $timestamp) {
            if ($timestamp < ($now - $period)) {
                unset($rateData['requests'][$key]);
            }
        }
        $rateData['requests'] = array_values($rateData['requests']);
    } else {
        $rateData = ['requests' => []];
    }

    // Check if rate limit is exceeded
    if (count($rateData['requests']) >= $maxRequests) {
        return false;
    }

    // Add current request
    $rateData['requests'][] = $now;

    // Save updated rate data
    file_put_contents($rateFile, json_encode($rateData));

    return true;
}
?>