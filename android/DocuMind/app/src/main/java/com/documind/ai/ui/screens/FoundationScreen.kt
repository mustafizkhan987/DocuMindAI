package com.documind.ai.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.documind.ai.ui.theme.DocuMindTheme
import kotlinx.coroutines.delay

/**
 * DocuMind AI — Foundation Screen
 *
 * Task 1: Project Foundation
 *
 * This screen demonstrates:
 * 1. App identity (name, subtitle)
 * 2. Backend connectivity status (simulated for Task 1)
 * 3. Feature roadmap preview
 * 4. Animated UI components
 *
 * In Task 4, the backend status will be replaced with a real
 * API call to GET /health using Retrofit.
 */

// Backend connection states
sealed class BackendStatus {
    object Checking : BackendStatus()
    object Connected : BackendStatus()
    object NotConnected : BackendStatus()
}

@Composable
fun FoundationScreen() {
    var contentVisible by remember { mutableStateOf(false) }
    var backendStatus by remember { mutableStateOf<BackendStatus>(BackendStatus.Checking) }

    // Animate content in on first launch
    LaunchedEffect(Unit) {
        delay(300)
        contentVisible = true
        // Simulate a backend check — Task 4 will replace this with a real API call
        delay(1500)
        // For Task 1, we show "Not Connected" since the server isn't running on device
        // This will become a real HTTP call in Task 4
        backendStatus = BackendStatus.NotConnected
    }

    // Animated background gradient
    val infiniteTransition = rememberInfiniteTransition(label = "bg_gradient")
    val gradientAlpha by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "gradient_alpha"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF0A0E1A),
                        Color(0xFF0D1B2E),
                        Color(0xFF0A1628),
                    )
                )
            )
    ) {
        // Decorative background circles
        Box(
            modifier = Modifier
                .size(300.dp)
                .align(Alignment.TopEnd)
                .background(
                    Color(0xFF00BCD4).copy(alpha = 0.05f * gradientAlpha),
                    shape = CircleShape
                )
        )
        Box(
            modifier = Modifier
                .size(200.dp)
                .align(Alignment.BottomStart)
                .background(
                    Color(0xFF1A237E).copy(alpha = 0.1f * gradientAlpha),
                    shape = CircleShape
                )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {

            // ── Logo / Icon ───────────────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800)) + slideInVertically(tween(800)) { it / 2 }
            ) {
                Box(
                    modifier = Modifier
                        .size(96.dp)
                        .clip(RoundedCornerShape(24.dp))
                        .background(
                            Brush.linearGradient(
                                colors = listOf(
                                    Color(0xFF00BCD4),
                                    Color(0xFF1A237E),
                                )
                            )
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "D",
                        fontSize = 48.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            // ── App Name ──────────────────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 200))
            ) {
                Text(
                    text = "DocuMind AI",
                    style = MaterialTheme.typography.displayMedium,
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // ── Subtitle ──────────────────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 400))
            ) {
                Text(
                    text = "AI-Powered\nDocument & Invoice Intelligence",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color(0xFF00BCD4),
                    textAlign = TextAlign.Center,
                    lineHeight = 24.sp
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // ── India Badge ───────────────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 500))
            ) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(50))
                        .background(Color(0xFF1A237E).copy(alpha = 0.5f))
                        .padding(horizontal = 16.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "🇮🇳  GST-Aware  •  Indian Business Intelligence",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color(0xFFB2EBF2),
                    )
                }
            }

            Spacer(modifier = Modifier.height(48.dp))

            // ── Backend Status Card ───────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 600))
            ) {
                BackendStatusCard(status = backendStatus)
            }

            Spacer(modifier = Modifier.height(32.dp))

            // ── Feature Preview Cards ─────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 800))
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    FeatureRow(
                        emoji = "📄",
                        title = "OCR + Document AI",
                        subtitle = "Extracts text from photos & PDFs",
                        status = "Coming in Task 7"
                    )
                    FeatureRow(
                        emoji = "🇮🇳",
                        title = "GSTIN Validation",
                        subtitle = "Validates GSTIN, PAN, state codes",
                        status = "Coming in Task 11"
                    )
                    FeatureRow(
                        emoji = "🧮",
                        title = "Invoice Math Check",
                        subtitle = "Independently verifies all calculations",
                        status = "Coming in Task 14"
                    )
                    FeatureRow(
                        emoji = "🔍",
                        title = "Duplicate Detection",
                        subtitle = "Finds duplicate invoices automatically",
                        status = "Coming in Task 19"
                    )
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            // ── Version Info ──────────────────────────────────────────────
            AnimatedVisibility(
                visible = contentVisible,
                enter = fadeIn(tween(800, delayMillis = 1000))
            ) {
                Text(
                    text = "v0.1.0 — Task 1: Project Foundation",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF546E7A),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun BackendStatusCard(status: BackendStatus) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF131929)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = "Backend API",
                    style = MaterialTheme.typography.titleSmall,
                    color = Color(0xFFB0BEC5),
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "http://10.0.2.2:8000",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF546E7A)
                )
            }

            when (status) {
                is BackendStatus.Checking -> {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(Color(0xFF263238))
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = "⏳ Checking...",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color(0xFF90A4AE)
                        )
                    }
                }

                is BackendStatus.Connected -> {
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(Color(0xFF1B5E20).copy(alpha = 0.3f))
                            .padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Connected",
                            tint = Color(0xFF4CAF50),
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = "Connected",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color(0xFF4CAF50)
                        )
                    }
                }

                is BackendStatus.NotConnected -> {
                    Row(
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(Color(0xFF7F1D1D).copy(alpha = 0.3f))
                            .padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = "Not Connected",
                            tint = Color(0xFFFF9800),
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = "Not Connected",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color(0xFFFF9800)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FeatureRow(
    emoji: String,
    title: String,
    subtitle: String,
    status: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF131929)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = emoji,
                fontSize = 28.sp,
                modifier = Modifier.width(40.dp)
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    color = Color(0xFFE3F2FD),
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF78909C)
                )
            }
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(50))
                    .background(Color(0xFF1E2A3F))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text(
                    text = status,
                    style = MaterialTheme.typography.labelSmall,
                    color = Color(0xFF00BCD4),
                    fontSize = 9.sp
                )
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0A0E1A)
@Composable
fun FoundationScreenPreview() {
    DocuMindTheme(darkTheme = true) {
        FoundationScreen()
    }
}
