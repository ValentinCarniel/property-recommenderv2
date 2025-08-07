// lib/auth.ts
import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import axios from "axios";

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET, // <-- clave secreta para cifrado

  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // URL corregida: sin /auth, porque en backend no tenés prefijo
          const response = await axios.post<{ access_token: string }>("http://localhost:8000/login", {
            email: credentials.email,
            password: credentials.password,
          });

          const { access_token } = response.data;

          return {
            id: credentials.email,
            email: credentials.email,
            name: credentials.email, // para cumplir con User
            accessToken: access_token,
          };
        } catch (error: any) {
          console.error("Login failed:", error.response?.data || error.message);
          return null;
        }
      },
    }),
  ],

  session: {
    strategy: "jwt",
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.accessToken = (user as any).accessToken;
      }
      return token;
    },

    async session({ session, token }) {
      session.user.id = token.id as string;
      session.user.email = token.email as string;
      session.user.accessToken = token.accessToken as string;
      return session;
    },
  },

  pages: {
    signIn: "/auth/signin",
  },
};
