import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import { AuthLayout } from '@/layouts/AuthLayout';
import { PublicLayout } from '@/layouts/PublicLayout';
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';
import { DashboardPage } from '@/pages/app/DashboardPage';
import { ResumeUploadPage } from '@/pages/app/ResumeUploadPage';
import { ResumeAnalysisPage } from '@/pages/app/ResumeAnalysisPage';
import { ResumeCoachPage } from '@/pages/app/ResumeCoachPage';
import { CareerRoadmapPage } from '@/pages/app/CareerRoadmapPage';

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [{ path: '/', element: <LandingPage /> }],
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      { index: true, element: <Navigate to="/auth/login" replace /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
    ],
  },
  {
    path: '/app',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'upload', element: <ResumeUploadPage /> },
      { path: 'analysis', element: <ResumeAnalysisPage /> },
      { path: 'coach', element: <ResumeCoachPage /> },
      { path: 'roadmap', element: <CareerRoadmapPage /> },
    ],
  },
]);
