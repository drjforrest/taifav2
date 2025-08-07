export default function InstitutionsPage() {
  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 
            className="text-4xl font-bold mb-6"
            style={{ color: "var(--color-foreground)" }}
          >
            Research Centers
          </h1>
          <p 
            className="text-lg max-w-2xl mx-auto mb-8"
            style={{ color: "var(--color-muted-foreground)" }}
          >
            Discover the universities, research institutions, and centers of excellence 
            advancing AI research across Africa.
          </p>
          <div 
            className="p-6 rounded-lg border"
            style={{ 
              backgroundColor: "var(--color-card)",
              borderColor: "var(--color-border)" 
            }}
          >
            <h2 
              className="text-xl font-semibold mb-4"
              style={{ color: "var(--color-card-foreground)" }}
            >
              Coming Soon
            </h2>
            <p 
              className="text-sm"
              style={{ color: "var(--color-muted-foreground)" }}
            >
              We're mapping research institutions, universities, and AI centers across Africa. 
              This will include research focus areas, publications, and collaboration networks.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
