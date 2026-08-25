package ir.news.app;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setAllowFileAccess(true);
        webView.setWebViewClient(new WebViewClient());
        webView.addJavascriptInterface(new Bridge(), "AndroidBridge");
        webView.setBackgroundColor(Color.parseColor("#070b12"));
        webView.loadUrl("file:///android_asset/index.html");
    }

    private int getStatusBarHeight() {
        int resId = getResources().getIdentifier("status_bar_height", "dimen", "android");
        if (resId > 0) return getResources().getDimensionPixelSize(resId);
        return 0;
    }

    private class Bridge {
        @JavascriptInterface
        public void setStatusBarPad(final int px) {
            runOnUiThread(new Runnable() {
                public void run() { webView.setPadding(0, px, 0, 0); }
            });
        }

        @JavascriptInterface
        public void hideStatusBar() {
            runOnUiThread(new Runnable() {
                public void run() {
                    getWindow().getDecorView().setSystemUiVisibility(
                        View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
                }
            });
        }

        @JavascriptInterface
        public void showStatusBar() {
            runOnUiThread(new Runnable() {
                public void run() {
                    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
                }
            });
        }

        @JavascriptInterface
        public void setWindowBg(final String color) {
            runOnUiThread(new Runnable() {
                public void run() {
                    try { webView.setBackgroundColor(Color.parseColor(color)); } catch (Exception e) {}
                }
            });
        }
    }
}
