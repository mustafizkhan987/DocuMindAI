package com.documind.ai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.documind.ai.ui.theme.DocuMindSuccess
import com.documind.ai.ui.theme.DocuMindWarning
import com.documind.ai.ui.theme.DocuMindError
import com.documind.ai.ui.theme.DocuMindSecondary

enum class StatusType {
    INFO, SUCCESS, WARNING, ERROR, BRAND
}

@Composable
fun StatusBadge(
    text: String,
    type: StatusType,
    modifier: Modifier = Modifier
) {
    val backgroundColor = when (type) {
        StatusType.INFO -> Color(0xFFE2E8F0)
        StatusType.SUCCESS -> DocuMindSuccess.copy(alpha = 0.15f)
        StatusType.WARNING -> DocuMindWarning.copy(alpha = 0.15f)
        StatusType.ERROR -> DocuMindError.copy(alpha = 0.15f)
        StatusType.BRAND -> DocuMindSecondary.copy(alpha = 0.15f)
    }
    
    val textColor = when (type) {
        StatusType.INFO -> Color(0xFF4A5568)
        StatusType.SUCCESS -> DocuMindSuccess
        StatusType.WARNING -> DocuMindWarning
        StatusType.ERROR -> DocuMindError
        StatusType.BRAND -> DocuMindSecondary
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(backgroundColor)
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Text(
            text = text,
            color = textColor,
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}
