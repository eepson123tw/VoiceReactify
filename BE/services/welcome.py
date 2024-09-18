def welcomePageTemplate():
    return """
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Parler TTS API</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #f0f4f8;
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
            }
            .navbar {
                background-color: #343a40;
            }
            .navbar-brand {
                color: #ffffff !important;
                font-weight: 700;
            }
            .welcome-container {
                background-color: #ffffff;
                padding: 60px 40px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
                margin: auto;
            }
            .welcome-container h1 {
                margin-bottom: 30px;
                font-size: 2.5rem;
                color: #343a40;
            }
            .welcome-container p {
                font-size: 1.2rem;
                color: #6c757d;
                margin-bottom: 30px;
            }
            .btn-custom {
                padding: 12px 30px;
                font-size: 1.1rem;
                border-radius: 30px;
                transition: background-color 0.3s, transform 0.3s;
            }
            .btn-custom:hover {
                background-color: #0056b3;
                transform: translateY(-2px);
            }
            .footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #343a40;
                color: #ffffff;
                text-align: center;
                padding: 10px 0;
            }
            @media (max-width: 576px) {
                .welcome-container {
                    padding: 40px 20px;
                }
                .welcome-container h1 {
                    font-size: 2rem;
                }
                .welcome-container p {
                    font-size: 1rem;
                }
                .btn-custom {
                    width: 100%;
                    padding: 12px 0;
                }
            }
        </style>
    </head>
    <body>
        <!-- Navigation Bar -->
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="#">Parler TTS API</a>
            </div>
        </nav>

        <!-- Welcome Section -->
        <div class="d-flex align-items-center justify-content-center" style="min-height: calc(100vh - 56px - 50px);">
		<div class="welcome-container">
			<h1>Welcome to Parler TTS API!</h1>
			<p>We offer advanced text-to-speech services to help you effortlessly generate natural and fluent voice content.</p>
			<a href="/docs" class="btn btn-primary btn-custom">Start Dive Generating Speech Docs</a>
		</div>
        </div>

        <!-- Footer -->
        <div class="footer">
            &copy; 2024 Parler TTS API. All rights reserved.
        </div>

        <!-- Bootstrap JS and dependencies -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

