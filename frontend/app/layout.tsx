import './globals.css';
export const metadata = { title: 'Actuarial Signal Radar', description: 'CNBS Honduras · Statistical signal exploration and evidence-aware investigation' };
export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="es"><body>{children}</body></html>;
}
