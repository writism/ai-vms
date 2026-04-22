"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { env } from "@/infrastructure/config/env";

export type WebRTCState = "idle" | "connecting" | "connected" | "failed";

export function useWebRTC(streamName: string | null) {
  const [state, setState] = useState<WebRTCState>("idle");
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);

  const connect = useCallback(async () => {
    if (!streamName) return;

    setState("connecting");

    try {
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
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
        if (pc.connectionState === "connected") setState("connected");
        if (pc.connectionState === "failed") setState("failed");
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
  }, [streamName]);

  const disconnect = useCallback(() => {
    pcRef.current?.close();
    pcRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setState("idle");
  }, []);

  useEffect(() => {
    return () => {
      pcRef.current?.close();
    };
  }, []);

  return { state, videoRef, connect, disconnect };
}
