<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $name = htmlspecialchars($_POST['name']);
    $email = htmlspecialchars($_POST['email']);
    $phone = htmlspecialchars($_POST['phone']);
    $service = htmlspecialchars($_POST['service']);
    $timeline = htmlspecialchars($_POST['timeline']);
    $address = htmlspecialchars($_POST['address']);
    $message = htmlspecialchars($_POST['message']);
    
    // Email configuration
    $to = "nickknight488@gmail.com";
    $subject = "New Service Request from " . $name;
    
    // Email body
    $email_body = "NEW SERVICE REQUEST from Knight Group Website:\n\n";
    $email_body .= "Name: " . $name . "\n";
    $email_body .= "Phone: " . $phone . "\n";
    $email_body .= "Email: " . $email . "\n";
    $email_body .= "Service Needed: " . $service . "\n";
    $email_body .= "Timeline: " . $timeline . "\n";
    $email_body .= "Address: " . $address . "\n\n";
    $email_body .= "Project Description:\n" . $message . "\n\n";
    $email_body .= "---\nSent from knightgroup.com contact form";
    
    // Email headers
    $headers = "From: " . $email . "\r\n";
    $headers .= "Reply-To: " . $email . "\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();
    
    // Send email
    if (mail($to, $subject, $email_body, $headers)) {
        echo json_encode(["success" => true, "message" => "Email sent successfully!"]);
    } else {
        echo json_encode(["success" => false, "message" => "Failed to send email."]);
    }
} else {
    echo json_encode(["success" => false, "message" => "Invalid request method."]);
}
?>
