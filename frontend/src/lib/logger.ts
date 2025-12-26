/**
 * Logging utility for Shafan frontend
 * Handles logging appropriately based on environment
 */

type LogLevel = 'info' | 'warn' | 'error' | 'debug'

interface LogContext {
  [key: string]: unknown
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development'

  /**
   * Log info messages (only in development)
   */
  info(message: string, context?: LogContext): void {
    if (this.isDevelopment) {
      console.info(`[INFO] ${message}`, context || '')
    }
  }

  /**
   * Log warning messages
   */
  warn(message: string, context?: LogContext): void {
    if (this.isDevelopment) {
      console.warn(`[WARN] ${message}`, context || '')
    } else {
      // In production, you could send to a monitoring service like Sentry
      this.sendToMonitoring('warn', message, context)
    }
  }

  /**
   * Log error messages
   */
  error(message: string, error?: Error | unknown, context?: LogContext): void {
    if (this.isDevelopment) {
      console.error(`[ERROR] ${message}`, error || '', context || '')
    } else {
      // In production, send to monitoring service
      this.sendToMonitoring('error', message, { error, ...context })
    }
  }

  /**
   * Log debug messages (only in development)
   */
  debug(message: string, context?: LogContext): void {
    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${message}`, context || '')
    }
  }

  /**
   * Send logs to monitoring service in production
   * This is a placeholder - implement with your monitoring service
   * (e.g., Sentry, LogRocket, Datadog, etc.)
   */
  private sendToMonitoring(
    level: LogLevel,
    message: string,
    context?: LogContext
  ): void {
    // Example: Send to Sentry, LogRocket, or your monitoring service
    // For now, we'll just use a minimal console output
    if (level === 'error') {
      console.error(message, context)
    }

    // TODO: Implement actual monitoring service integration
    // Example with Sentry:
    // import * as Sentry from '@sentry/nextjs';
    // Sentry.captureMessage(message, {
    //   level: level as Sentry.SeverityLevel,
    //   extra: context,
    // });
  }
}

// Export singleton instance
export const logger = new Logger()
