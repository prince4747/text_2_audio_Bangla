<?php
// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once 'config.php';

header('Content-Type: application/json');

// Allow from any origin
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

// Function to send response
function sendResponse($status, $message, $data = null) {
    $response = [
        'status' => $status,
        'message' => $message,
        'data' => $data
    ];
    echo json_encode($response);
    exit;
}

// Check if it's a POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    sendResponse('error', 'Only POST method is allowed');
}

// Check for API key
$api_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';

if (empty($api_key)) {
    sendResponse('error', 'API key is required');
}

if ($api_key !== API_KEY) {
    sendResponse('error', 'Invalid API key');
}

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

// Validate input
if (!isset($input['phone']) || !isset($input['message']) || !isset($input['uuid'])) {
    sendResponse('error', 'Phone, message, and uuid are required');
}

$phone = trim($input['phone']);
$message = trim($input['message']);
$uuid = trim($input['uuid']);

// Validate UUID (numbers only)
if (!preg_match('/^\d+$/', $uuid)) {
    sendResponse('error', 'Invalid UUID format. UUID must contain only numbers');
}

// Validate phone (basic validation)
if (!preg_match('/^\+?[1-9]\d{1,14}$/', $phone)) {
    sendResponse('error', 'Invalid phone number format');
}

// Validate message
if (empty($message)) {
    sendResponse('error', 'Message cannot be empty');
}

// Prepare data for Python script
$pythonInput = json_encode([
    'phone' => $phone,
    'message' => $message,
    'uuid' => $uuid
]);

// Call Python script with proper JSON escaping
$command = 'python3 ' . __DIR__ . '/text_to_speech.py ' . escapeshellarg($pythonInput) . ' 2>&1';
$output = shell_exec($command);

// Debug logging
error_log("Python command: " . $command);
error_log("Python output: " . $output);

// Parse Python script output
$result = json_decode($output, true);

if (!$result) {
    error_log("Failed to decode Python output: " . $output);
    sendResponse('error', 'Failed to decode Python output: ' . $output);
}

if ($result['status'] === 'error') {
    error_log("Python script error: " . $result['message']);
    sendResponse('error', $result['message']);
}

// Send success response with audio file information
$response_data = [
    'phone' => $phone,
    'message' => $message,
    'audio_file' => isset($result['audio_file']) ? $result['audio_file'] : null,
    'timestamp' => date('Y-m-d H:i:s')
];

sendResponse('success', 'Message processed successfully', $response_data);
?>
