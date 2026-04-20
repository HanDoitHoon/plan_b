import {Link, useLocation} from "react-router-dom";

export default function Layout({ children }) {
    const location = useLocation();

    const menus = [
        {path:"/", label: "Home"},
        {path:"/dashboard", label: "Dashboard"},
        {path:"/analysis", label: "Analysis"},
        {path:"/predict", label: "Predict"},
    ];

    return (
        <div style={styles.wrapper}>
            <aside style={styles.sidebar}>
                <h2 style={styles.logo}>Plan_B</h2>
                <nav style={styles.nav}>
                    {menus.map((menu) => (
                        <Link
                        key={menu.path}
                        to={menu.path}
                        style={{
                            ...styles.link,
                            ...(location.pathname === menu.path ? styles.activeLink : {}),
                            }}
                        >
                            {menu.label}
                        </Link>
                    ))}
                </nav>
            </aside>

            <main style = {styles.main}>{children}</main>
        </div>
    );
}
const styles = {
  wrapper: {
    minHeight: "100vh",
    backgroundColor: "#f7f8fa",
  },
  sidebar: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "220px",
    height: "100vh",
    backgroundColor: "#111827",
    color: "white",
    padding: "24px 16px",
    boxSizing: "border-box",
    overflowY: "auto",
  },
  logo: {
    margin: "0 0 24px 0",
    fontSize: "24px",
  },
  nav: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  link: {
    color: "#d1d5db",
    textDecoration: "none",
    padding: "10px 12px",
    borderRadius: "8px",
  },
  activeLink: {
    backgroundColor: "#2563eb",
    color: "white",
  },
  main: {
    marginLeft: "220px",
    minHeight: "100vh",
    padding: "32px",
    boxSizing: "border-box",
  },
};