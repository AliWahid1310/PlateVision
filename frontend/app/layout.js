import './globals.css';

export const metadata = {
  title: 'ANPR & Vehicle Detection AI | Modern Computer Vision',
  description: 'Automated License Plate Recognition and Vehicle Classification System built with YOLOv8, OpenCV, and EasyOCR.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="ambient-bg">
          <div className="ambient-blob-1" />
          <div className="ambient-blob-2" />
          <div className="ambient-grid" />
        </div>
        {children}
      </body>
    </html>
  );
}
