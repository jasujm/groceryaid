import React from "react";
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats } from "html5-qrcode";

const html5QrcodeId = "html5-qrcode-region";

export interface Props {
  onScanBarcode: (ean: string) => void;
}

export default function BarcodeScanner({ onScanBarcode }: Props) {
  React.useEffect(() => {
    const html5Qrcode = new Html5QrcodeScanner(
      html5QrcodeId,
      {
        fps: 10,
        qrbox: 300,
        formatsToSupport: [Html5QrcodeSupportedFormats.EAN_13],
        supportedScanTypes: [],
      },
      false
    );
    html5Qrcode.render(onScanBarcode, () => {});
    return () => {
      // TODO: display errors
      html5Qrcode.clear();
    };
  }, [onScanBarcode]);

  return <div id={html5QrcodeId} className="barcode-scanner" />;
}
