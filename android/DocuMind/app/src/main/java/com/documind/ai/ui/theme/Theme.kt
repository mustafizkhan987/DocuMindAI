package com.documind.ai.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// DocuMind AI Brand Colors
// Primary: Deep Indigo/Blue — trust, intelligence, professionalism
val DocuMindPrimary = Color(0xFF1A237E)          // Deep Indigo
val DocuMindPrimaryVariant = Color(0xFF283593)   // Indigo 800
val DocuMindSecondary = Color(0xFF00BCD4)        // Cyan — modern, AI-forward
val DocuMindSecondaryVariant = Color(0xFF0097A7) // Cyan 700
val DocuMindAccent = Color(0xFF26C6DA)           // Cyan 400

// Semantic Colors
val DocuMindSuccess = Color(0xFF4CAF50)          // Green — validated
val DocuMindWarning = Color(0xFFFF9800)          // Orange — attention needed
val DocuMindError = Color(0xFFF44336)            // Red — issue detected

// Dark Theme Backgrounds
val DarkBackground = Color(0xFF0A0E1A)           // Very dark navy
val DarkSurface = Color(0xFF131929)              // Dark card surface
val DarkSurfaceVariant = Color(0xFF1E2A3F)       // Slightly lighter surface

private val DarkColorScheme = darkColorScheme(
    primary = DocuMindSecondary,
    onPrimary = Color(0xFF003040),
    primaryContainer = Color(0xFF004D61),
    onPrimaryContainer = Color(0xFFB2EBF2),
    secondary = DocuMindAccent,
    onSecondary = Color(0xFF002B36),
    secondaryContainer = Color(0xFF004D5C),
    onSecondaryContainer = Color(0xFFB2EBF2),
    tertiary = Color(0xFF80DEEA),
    background = DarkBackground,
    onBackground = Color(0xFFE3F2FD),
    surface = DarkSurface,
    onSurface = Color(0xFFE3F2FD),
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = Color(0xFFB0BEC5),
    error = DocuMindError,
    onError = Color.White,
)

private val LightColorScheme = lightColorScheme(
    primary = DocuMindPrimary,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE8EAF6),
    onPrimaryContainer = DocuMindPrimary,
    secondary = Color(0xFF0097A7),
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFE0F7FA),
    onSecondaryContainer = Color(0xFF006064),
    tertiary = Color(0xFF00838F),
    background = Color(0xFFF5F7FF),
    onBackground = Color(0xFF0A0E1A),
    surface = Color.White,
    onSurface = Color(0xFF1A1A2E),
    surfaceVariant = Color(0xFFF0F2FF),
    onSurfaceVariant = Color(0xFF3D4560),
    error = DocuMindError,
    onError = Color.White,
)

/**
 * DocuMind AI Material3 Theme
 *
 * Uses dynamic color on Android 12+ for a modern adaptive experience.
 * Falls back to our brand color scheme on older Android versions.
 */
@Composable
fun DocuMindTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
