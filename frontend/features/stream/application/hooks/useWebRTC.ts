"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { env } from "@/infrastructure/config/env";

export type WebRTCState = "idle" | "connecting" | "connected" | "failed";

export function useWebRTC(streamName: string | null) {
  const [state, setState] = useState<WebRTCState>("idle");
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);

  const cleanup = useCallback(() => {
    const pc = pcRef.current;
    if (pc) {
      pc.ontrack = null;
      pc.onconnectionstatechange = null;
      pc.close();
      pcRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);

  const connect = useCallback(async () => {
    if (!streamName) return;

    cleanup();
    setState("connecting");

    try {
      const stunUrl = env.turnUrl.replace(/^turn:/, "stun:");
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: stunUrl },
          {
            urls: env.turnUrl,
            username: env.turnUser,
            credential: env.turnPass,
          },
        ],
        iceCandidatePoolSize: 4,
      });
      pcRef.current = pc;

      pc.addTransceiver("video", { direction: "recvonly" });
      pc.addTransceiver("audio", { direction: "recvonly" });

      pc.ontrack = (event) => {
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0];
        }
      };

      pc.onconnectionstatechange = () => {
        const s = pc.connectionState;
        if (s === "connected") setState("connected");
        if (s === "failed" || s === "disconnected") setState("failed");
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const res = await fetch(
        `${env.go2rtcUrl}/api/webrtc?src=${encodeURIComponent(streamName)}`,
        {
          method: "POST",
          body: offer.sdp,
          headers: { "Content-Type": "application/sdp" },
        },
      );

      if (!res.ok) {
        setState("failed");
        return;
      }

      const sdpAnswer = await res.text();
      await pc.setRemoteDescription(
        new RTCSessionDescription({ type: "answer", sdp: sdpAnswer }),
      );
    } catch {
      setState("failed");
    }
  }, [streamName, cleanup]);

  const disconnect = useCallback(() => {
    cleanup();
    setState("idle");
  }, [cleanup]);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return { state, videoRef, connect, disconnect };
}
