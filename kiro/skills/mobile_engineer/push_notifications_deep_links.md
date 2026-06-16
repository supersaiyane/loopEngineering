---
id: push_notifications_deep_links
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - push-notifications
  - deep-links
  - mobile
  - fcm
  - apns
when_to_use: "When implementing push notifications or deep linking in a mobile app, connecting notification taps to specific app screens."
inputs:
  - notification types
  - deep link URL scheme
  - platform (iOS/Android/both)
outputs:
  - FCM/APNs setup
  - notification handler
  - deep link routing
  - permission flow
---

> "A push notification is a promise to the user. A deep link is the delivery."

## Expo Notifications Setup

```typescript
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";

// Configure how notifications appear when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null;   // simulators can't receive push

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") return null;   // user denied

  const token = (await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas?.projectId,
  })).data;

  // Send token to your backend
  await api.registerPushToken({ token, platform: Platform.OS });
  return token;
}
```

## Notification Handler + Deep Link

```typescript
// In your root layout
export default function RootLayout() {
  const router = useRouter();

  useEffect(() => {
    // Handle notification tap when app is backgrounded/killed
    const subscription = Notifications.addNotificationResponseReceivedListener((response) => {
      const deepLink = response.notification.request.content.data?.deepLink as string;
      if (deepLink) router.push(deepLink);
    });
    return () => subscription.remove();
  }, []);

  // Handle deep links from URL scheme
  useEffect(() => {
    const handleUrl = ({ url }: { url: string }) => {
      // myapp://orders/123 → /orders/123
      const path = url.replace("myapp://", "/");
      router.push(path);
    };
    const subscription = Linking.addEventListener("url", handleUrl);
    return () => subscription.remove();
  }, []);
}
```

## Soft Permission Prompt Pattern

```typescript
// Show value proposition BEFORE OS permission dialog
function NotificationPermissionPrompt({ onAccept, onDecline }) {
  return (
    <Modal>
      <Text>Get instant order updates — we'll notify you when orders ship.</Text>
      <Button title="Enable notifications" onPress={onAccept} />
      <Button title="Maybe later" onPress={onDecline} />
    </Modal>
  );
}
// Show OS dialog only after user taps "Enable" — avoids wasting the one-time OS prompt
```

## Validation Checklist

- [ ] Permission requested with soft prompt before OS dialog
- [ ] Push token sent to backend and stored per device
- [ ] Notification taps route to correct screen via deep link
- [ ] Foreground notification handler configured
- [ ] Token refresh handled (`Notifications.addPushTokenListener`)
